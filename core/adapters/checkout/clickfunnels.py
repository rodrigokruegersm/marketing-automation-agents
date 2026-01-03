"""
ClickFunnels Adapter
Integration with ClickFunnels 2.0 checkout/funnel platform
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics,
    PaymentStatus, ProductType
)


class ClickFunnelsAdapter(BaseCheckoutAdapter):
    """
    Adapter for ClickFunnels 2.0 platform.

    ClickFunnels API Documentation: https://developers.clickfunnels.com/

    Usage:
        adapter = ClickFunnelsAdapter(
            api_key="your_api_key",
            workspace_id="your_workspace_id"
        )
        products = adapter.get_products()
        sales = adapter.get_sales(start_date=datetime(2024, 1, 1))
    """

    platform_name = "clickfunnels"
    base_url = "https://api.clickfunnels.com/api/v2"

    def __init__(
        self,
        api_key: str,
        workspace_id: str = "",
        team_id: str = "",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.workspace_id = workspace_id
        self.team_id = team_id

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict:
        """Make API request to ClickFunnels"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=params)
            else:
                response = requests.request(
                    method, url, headers=headers, json=params
                )

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {'error': str(e), 'status_code': e.response.status_code}
        except Exception as e:
            return {'error': str(e)}

    def test_connection(self) -> Dict:
        """Test API connection"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}

        # Test with workspaces endpoint
        endpoint = '/workspaces' if not self.workspace_id else f'/workspaces/{self.workspace_id}'
        result = self._request(endpoint)

        return {
            'success': 'error' not in result,
            'platform': self.platform_name,
            'response': result
        }

    def get_products(self) -> List[Product]:
        """Fetch all products from ClickFunnels"""
        if not self.workspace_id:
            return []

        result = self._request(f'/workspaces/{self.workspace_id}/products')

        if 'error' in result:
            return []

        products = []
        items = result if isinstance(result, list) else result.get('data', [])
        for item in items:
            products.append(self._parse_product(item))

        return products

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch a specific product"""
        if not self.workspace_id:
            return None

        result = self._request(
            f'/workspaces/{self.workspace_id}/products/{product_id}'
        )

        if 'error' in result:
            return None

        return self._parse_product(result)

    def _parse_product(self, data: Dict) -> Product:
        """Parse ClickFunnels product data"""
        # Handle nested attributes
        attrs = data.get('attributes', data)

        # Get price from variants or default
        variants = attrs.get('variants', [])
        price = 0.0
        if variants:
            first_variant = variants[0] if isinstance(variants, list) else {}
            price = float(first_variant.get('price', {}).get('amount', 0)) / 100
        else:
            price = float(attrs.get('default_price', 0)) / 100

        # Determine product type
        product_type = ProductType.COURSE
        if attrs.get('is_physical'):
            product_type = ProductType.PHYSICAL
        elif attrs.get('is_subscription'):
            product_type = ProductType.MEMBERSHIP

        return Product(
            id=str(data.get('id', attrs.get('id', ''))),
            name=attrs.get('name', ''),
            platform=self.platform_name,
            price=price,
            currency=attrs.get('currency', 'USD'),
            type=product_type,
            description=attrs.get('description', ''),
            platform_fee_percent=0.0,  # CF doesn't take % on payments
            funnel_tag=attrs.get('funnel_tag', ''),
            raw_data=data
        )

    def get_funnels(self) -> List[Dict]:
        """Fetch all funnels (sales funnels)"""
        if not self.workspace_id:
            return []

        result = self._request(f'/workspaces/{self.workspace_id}/funnels')

        if 'error' in result:
            return []

        return result if isinstance(result, list) else result.get('data', [])

    def get_funnel(self, funnel_id: str) -> Optional[Dict]:
        """Fetch a specific funnel"""
        if not self.workspace_id:
            return None

        result = self._request(
            f'/workspaces/{self.workspace_id}/funnels/{funnel_id}'
        )

        if 'error' in result:
            return None

        return result

    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """Fetch offers/pages from ClickFunnels funnels"""
        funnels = self.get_funnels()

        if not funnels:
            return []

        offers = []
        for funnel in funnels:
            funnel_attrs = funnel.get('attributes', funnel)
            funnel_id = funnel.get('id', funnel_attrs.get('id', ''))

            # Get pages for this funnel
            pages_result = self._request(
                f'/workspaces/{self.workspace_id}/funnels/{funnel_id}/pages'
            )

            if 'error' in pages_result:
                continue

            pages = pages_result if isinstance(pages_result, list) else pages_result.get('data', [])

            for page in pages:
                page_attrs = page.get('attributes', page)

                # Only include checkout/order pages
                page_type = page_attrs.get('page_type', '')
                if page_type not in ['checkout', 'order_form', 'upsell', 'downsell', 'oto']:
                    continue

                offer = Offer(
                    id=str(page.get('id', page_attrs.get('id', ''))),
                    name=page_attrs.get('name', ''),
                    product_id=str(product_id or funnel_id),
                    platform=self.platform_name,
                    price=float(page_attrs.get('price', 0)),
                    checkout_url=page_attrs.get('url', ''),
                    is_upsell=page_type in ['upsell', 'oto'],
                    funnel_tag=funnel_attrs.get('name', ''),
                    funnel_stage='main' if page_type == 'checkout' else page_type,
                    raw_data=page
                )
                offers.append(offer)

        return offers

    def get_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Fetch orders from ClickFunnels"""
        if not self.workspace_id:
            return []

        params = {'per_page': 100}

        if status:
            params['filter[status]'] = status

        if start_date:
            params['filter[created_at_gte]'] = start_date.isoformat()
        if end_date:
            params['filter[created_at_lte]'] = end_date.isoformat()

        result = self._request(
            f'/workspaces/{self.workspace_id}/orders',
            params=params
        )

        if 'error' in result:
            return []

        return result if isinstance(result, list) else result.get('data', [])

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Sale]:
        """Fetch sales/orders from ClickFunnels"""
        # Map PaymentStatus to CF status
        cf_status = None
        if status:
            status_map = {
                PaymentStatus.APPROVED: 'paid',
                PaymentStatus.PENDING: 'pending',
                PaymentStatus.REFUNDED: 'refunded',
                PaymentStatus.CANCELLED: 'canceled'
            }
            cf_status = status_map.get(status)

        orders = self.get_orders(start_date, end_date, cf_status)

        sales = []
        for order in orders:
            sale = self._parse_sale(order)

            # Filter by product if specified
            if product_id and sale.product_id != product_id:
                continue

            sales.append(sale)

        return sales

    def _parse_sale(self, data: Dict) -> Sale:
        """Parse ClickFunnels order as sale"""
        attrs = data.get('attributes', data)

        # Map CF status to PaymentStatus
        status_str = attrs.get('status', '').lower()
        status_map = {
            'paid': PaymentStatus.APPROVED,
            'complete': PaymentStatus.APPROVED,
            'completed': PaymentStatus.APPROVED,
            'pending': PaymentStatus.PENDING,
            'refunded': PaymentStatus.REFUNDED,
            'canceled': PaymentStatus.CANCELLED,
            'cancelled': PaymentStatus.CANCELLED,
            'failed': PaymentStatus.CANCELLED
        }
        payment_status = status_map.get(status_str, PaymentStatus.PENDING)

        # Get amount
        amount = float(attrs.get('total_amount', 0)) / 100

        # Parse date
        created_str = attrs.get('created_at', '')
        created_at = None
        if created_str:
            try:
                created_at = datetime.fromisoformat(
                    created_str.replace('Z', '+00:00')
                )
            except Exception:
                pass

        # Get contact/customer info
        contact = attrs.get('contact', {}) or {}

        # Get product info from line items
        line_items = attrs.get('line_items', []) or []
        product_id = ''
        product_name = ''
        if line_items:
            first_item = line_items[0]
            product_id = str(first_item.get('product_id', ''))
            product_name = first_item.get('name', '')

        # Extract UTM from origination data
        origination = attrs.get('origination', {}) or {}

        return Sale(
            id=str(data.get('id', attrs.get('id', ''))),
            platform=self.platform_name,
            product_id=product_id,
            product_name=product_name,
            amount=amount,
            currency=attrs.get('currency', 'USD'),
            status=payment_status,
            payment_method=attrs.get('payment_method_type', ''),
            customer_email=contact.get('email_address', ''),
            customer_name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            utm_source=origination.get('utm_source', ''),
            utm_medium=origination.get('utm_medium', ''),
            utm_campaign=origination.get('utm_campaign', ''),
            utm_content=origination.get('utm_content', ''),
            funnel_tag=attrs.get('funnel_name', ''),
            created_at=created_at,
            platform_fee=0,  # CF doesn't take transaction fees
            net_amount=amount,
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

            # Group by funnel
            if sale.funnel_tag:
                if sale.funnel_tag not in metrics.by_funnel:
                    metrics.by_funnel[sale.funnel_tag] = {'sales': 0, 'revenue': 0}
                metrics.by_funnel[sale.funnel_tag]['sales'] += 1
                metrics.by_funnel[sale.funnel_tag]['revenue'] += sale.amount

            # Group by UTM source
            if sale.utm_source:
                if sale.utm_source not in metrics.by_utm_source:
                    metrics.by_utm_source[sale.utm_source] = {'sales': 0, 'revenue': 0}
                metrics.by_utm_source[sale.utm_source]['sales'] += 1
                metrics.by_utm_source[sale.utm_source]['revenue'] += sale.amount

            # Group by UTM campaign
            if sale.utm_campaign:
                if sale.utm_campaign not in metrics.by_utm_campaign:
                    metrics.by_utm_campaign[sale.utm_campaign] = {'sales': 0, 'revenue': 0}
                metrics.by_utm_campaign[sale.utm_campaign]['sales'] += 1
                metrics.by_utm_campaign[sale.utm_campaign]['revenue'] += sale.amount

        metrics.calculate_derived()
        return metrics

    def get_contacts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch contacts/leads from ClickFunnels"""
        if not self.workspace_id:
            return []

        params = {'per_page': 100}

        if start_date:
            params['filter[created_at_gte]'] = start_date.isoformat()
        if end_date:
            params['filter[created_at_lte]'] = end_date.isoformat()

        result = self._request(
            f'/workspaces/{self.workspace_id}/contacts',
            params=params
        )

        if 'error' in result:
            return []

        return result if isinstance(result, list) else result.get('data', [])

    def get_funnel_stats(self, funnel_id: str) -> Dict:
        """Get statistics for a specific funnel"""
        if not self.workspace_id:
            return {}

        result = self._request(
            f'/workspaces/{self.workspace_id}/funnels/{funnel_id}/stats'
        )

        if 'error' in result:
            return {}

        return result
