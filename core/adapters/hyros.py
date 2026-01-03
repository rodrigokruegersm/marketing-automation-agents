"""
Hyros Adapter
Integration with Hyros analytics and attribution platform
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import requests


@dataclass
class HyrosSale:
    """Hyros sale/transaction data"""
    id: str
    order_id: str
    amount: float = 0.0
    qualified: bool = True
    recurring: bool = False
    quantity: int = 1
    created_at: Optional[datetime] = None
    lead_email: str = ""
    lead_name: str = ""
    lead_phone: str = ""
    first_source: str = ""
    first_source_tag: str = ""
    last_source: str = ""
    last_source_tag: str = ""
    ad_platform: str = ""
    ad_account_id: str = ""
    ad_id: str = ""
    tags: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)


@dataclass
class HyrosLead:
    """Hyros lead data"""
    id: str
    email: str
    created_at: Optional[datetime] = None
    first_name: str = ""
    last_name: str = ""
    phone_numbers: List[str] = field(default_factory=list)
    ips: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)


@dataclass
class HyrosSource:
    """Hyros attribution source"""
    name: str
    tag: str
    organic: bool = False
    disregarded: bool = False
    platform: str = ""
    ad_account_id: str = ""
    ad_source_id: str = ""
    category: str = ""
    goal: str = ""
    raw_data: Dict = field(default_factory=dict)


class HyrosAdapter:
    """
    Adapter for Hyros analytics and attribution platform.

    Hyros provides detailed funnel analytics, checkout tracking,
    revenue attribution, and advanced tracking data.

    Usage:
        adapter = HyrosAdapter(api_key="your_api_key")
        sales = adapter.get_sales()
        leads = adapter.get_leads()
        sources = adapter.get_sources()
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.hyros.com/v1/api/v1.0"

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request using API-Key header authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'API-Key': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=params, timeout=30)

            if response.status_code == 401:
                return {'error': 'Unauthorized - invalid API key'}
            elif response.status_code == 404:
                return {'error': f'Endpoint not found: {endpoint}'}

            return response.json()
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except Exception as e:
            return {'error': str(e)}

    def is_configured(self) -> bool:
        """Check if Hyros is properly configured"""
        return bool(self.api_key)

    def test_connection(self) -> Dict:
        """Test API connection by fetching user info"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured - API key required'}

        result = self._request('/user-info')

        if 'error' in result:
            return {'success': False, 'error': result['error']}

        user_profile = result.get('result', {}).get('userProfile', {})
        return {
            'success': True,
            'platform': 'hyros',
            'account_email': user_profile.get('email', ''),
            'account_name': f"{user_profile.get('firstName', '')} {user_profile.get('lastName', '')}".strip(),
            'response': 'Connected successfully'
        }

    def get_user_info(self) -> Dict:
        """Get account user information"""
        result = self._request('/user-info')
        if 'error' in result:
            return {}
        return result.get('result', {}).get('userProfile', {})

    def get_sales(
        self,
        limit: int = 100,
        page_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HyrosSale]:
        """
        Fetch sales/transactions from Hyros.

        Args:
            limit: Number of results per page
            page_id: Pagination cursor
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of HyrosSale objects
        """
        params = {'limit': limit}
        if page_id:
            params['pageId'] = page_id

        result = self._request('/sales', params)

        if 'error' in result:
            return []

        sales = []
        for item in result.get('result', []):
            sale = self._parse_sale(item)

            # Date filtering
            if start_date and sale.created_at and sale.created_at < start_date:
                continue
            if end_date and sale.created_at and sale.created_at > end_date:
                continue

            sales.append(sale)

        return sales

    def _parse_sale(self, data: Dict) -> HyrosSale:
        """Parse Hyros sale data"""
        # Parse creation date
        created_str = data.get('creationDate', '')
        created_at = None
        if created_str:
            try:
                # Format: "Sat Jan 03 11:39:31 UTC 2026"
                created_at = datetime.strptime(created_str, '%a %b %d %H:%M:%S %Z %Y')
            except:
                try:
                    created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                except:
                    pass

        # Extract lead info
        lead = data.get('lead', {}) or {}
        lead_name = f"{lead.get('firstName', '')} {lead.get('lastName', '')}".strip()

        # Extract source info
        first_source = data.get('firstSource', {}) or {}
        last_source = data.get('lastSource', {}) or {}

        # Get ad platform info
        ad_source = first_source.get('adSource', {}) or {}

        return HyrosSale(
            id=data.get('id', ''),
            order_id=data.get('orderId', ''),
            amount=float(data.get('amount', 0) or 0),
            qualified=data.get('qualified', True),
            recurring=data.get('recurring', False),
            quantity=data.get('quantity', 1),
            created_at=created_at,
            lead_email=lead.get('email', ''),
            lead_name=lead_name,
            lead_phone=lead.get('phoneNumbers', [''])[0] if lead.get('phoneNumbers') else '',
            first_source=first_source.get('name', ''),
            first_source_tag=first_source.get('tag', ''),
            last_source=last_source.get('name', ''),
            last_source_tag=last_source.get('tag', ''),
            ad_platform=ad_source.get('platform', ''),
            ad_account_id=ad_source.get('adAccountId', ''),
            ad_id=ad_source.get('adSourceId', ''),
            tags=lead.get('tags', []),
            raw_data=data
        )

    def get_leads(
        self,
        limit: int = 100,
        page_id: Optional[str] = None
    ) -> List[HyrosLead]:
        """Fetch leads from Hyros"""
        params = {'limit': limit}
        if page_id:
            params['pageId'] = page_id

        result = self._request('/leads', params)

        if 'error' in result:
            return []

        leads = []
        for item in result.get('result', []):
            leads.append(self._parse_lead(item))

        return leads

    def _parse_lead(self, data: Dict) -> HyrosLead:
        """Parse Hyros lead data"""
        created_str = data.get('creationDate', '')
        created_at = None
        if created_str:
            try:
                created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except:
                pass

        return HyrosLead(
            id=data.get('id', ''),
            email=data.get('email', ''),
            created_at=created_at,
            first_name=data.get('firstName', ''),
            last_name=data.get('lastName', ''),
            phone_numbers=data.get('phoneNumbers', []),
            ips=data.get('ips', []),
            tags=data.get('tags', []),
            raw_data=data
        )

    def get_sources(self, limit: int = 100) -> List[HyrosSource]:
        """Fetch attribution sources"""
        result = self._request('/sources', {'limit': limit})

        if 'error' in result:
            return []

        sources = []
        for item in result.get('result', []):
            sources.append(self._parse_source(item))

        return sources

    def _parse_source(self, data: Dict) -> HyrosSource:
        """Parse Hyros source data"""
        ad_source = data.get('adSource', {}) or {}
        category = data.get('category', {}) or {}
        goal = data.get('goal', {}) or {}

        return HyrosSource(
            name=data.get('name', ''),
            tag=data.get('tag', ''),
            organic=data.get('organic', False),
            disregarded=data.get('disregarded', False),
            platform=ad_source.get('platform', ''),
            ad_account_id=ad_source.get('adAccountId', ''),
            ad_source_id=ad_source.get('adSourceId', ''),
            category=category.get('name', ''),
            goal=goal.get('name', ''),
            raw_data=data
        )

    def get_tags(self) -> List[str]:
        """Fetch all tags"""
        result = self._request('/tags')

        if 'error' in result:
            return []

        return result.get('result', [])

    def get_ads(self, limit: int = 100) -> List[Dict]:
        """Fetch ads data"""
        result = self._request('/ads', {'limit': limit})

        if 'error' in result:
            return []

        return result.get('result', [])

    def get_calls(self, limit: int = 100) -> List[Dict]:
        """Fetch calls data"""
        result = self._request('/calls', {'limit': limit})

        if 'error' in result:
            return []

        return result.get('result', [])

    def get_attribution_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get a summary of attribution data.

        Returns aggregated data by source/platform.
        """
        sales = self.get_sales(limit=1000, start_date=start_date, end_date=end_date)

        summary = {
            'total_sales': len(sales),
            'total_revenue': sum(s.amount for s in sales),
            'by_platform': {},
            'by_source': {},
            'qualified_sales': sum(1 for s in sales if s.qualified),
            'recurring_sales': sum(1 for s in sales if s.recurring)
        }

        for sale in sales:
            # Group by platform
            platform = sale.ad_platform or 'organic'
            if platform not in summary['by_platform']:
                summary['by_platform'][platform] = {'sales': 0, 'revenue': 0}
            summary['by_platform'][platform]['sales'] += 1
            summary['by_platform'][platform]['revenue'] += sale.amount

            # Group by source
            source = sale.first_source or 'unknown'
            if source not in summary['by_source']:
                summary['by_source'][source] = {'sales': 0, 'revenue': 0}
            summary['by_source'][source]['sales'] += 1
            summary['by_source'][source]['revenue'] += sale.amount

        return summary

    def match_meta_campaign(self, meta_ad_account_id: str) -> List[HyrosSale]:
        """
        Find Hyros sales attributed to a specific Meta ad account.

        Args:
            meta_ad_account_id: Meta Ads account ID (without 'act_' prefix)

        Returns:
            List of sales attributed to this Meta account
        """
        sales = self.get_sales(limit=1000)

        # Clean the ad account ID
        clean_id = meta_ad_account_id.replace('act_', '')

        matched = []
        for sale in sales:
            if sale.ad_account_id == clean_id and sale.ad_platform == 'FACEBOOK':
                matched.append(sale)

        return matched
