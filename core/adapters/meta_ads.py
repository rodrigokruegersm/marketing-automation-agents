"""
Meta Ads Adapter
Unified interface for Meta Ads API
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MetaAdsConfig:
    """Configuration for Meta Ads API"""
    access_token: str
    ad_account_id: str
    api_version: str = "v18.0"

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"


class MetaAdsAdapter:
    """
    Adapter for Meta Ads API.

    Usage:
        adapter = MetaAdsAdapter(
            access_token="your_token",
            ad_account_id="act_123456"
        )
        insights = adapter.get_account_insights(date_preset='last_7d')
        campaigns = adapter.get_campaigns()
    """

    def __init__(self, access_token: str, ad_account_id: str, api_version: str = "v18.0"):
        self.config = MetaAdsConfig(
            access_token=access_token,
            ad_account_id=ad_account_id,
            api_version=api_version
        )

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request"""
        url = f"{self.config.base_url}{endpoint}"
        params = params or {}
        params['access_token'] = self.config.access_token

        try:
            if method == "GET":
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, params=params)

            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def get_account_insights(
        self,
        date_preset: str = 'last_7d',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Fetch account-level insights.

        Args:
            date_preset: Meta date preset (last_7d, last_30d, etc.)
            start_date: Custom start date
            end_date: Custom end date

        Returns:
            Dict with metrics or None on error
        """
        params = {
            'fields': ','.join([
                'spend', 'impressions', 'reach', 'frequency',
                'cpm', 'clicks', 'cpc', 'ctr',
                'actions', 'action_values', 'cost_per_action_type',
                'purchase_roas'
            ])
        }

        if start_date and end_date:
            params['time_range'] = json.dumps({
                'since': start_date.strftime('%Y-%m-%d'),
                'until': end_date.strftime('%Y-%m-%d')
            })
        else:
            params['date_preset'] = date_preset

        result = self._request(f"/{self.config.ad_account_id}/insights", params)

        if 'data' in result and result['data']:
            return result['data'][0]
        return None

    def get_campaigns(
        self,
        status_filter: Optional[List[str]] = None,
        include_insights: bool = True,
        date_preset: str = 'last_7d'
    ) -> List[Dict]:
        """
        Fetch campaigns with optional insights.

        Args:
            status_filter: Filter by status (ACTIVE, PAUSED, etc.)
            include_insights: Include insights data
            date_preset: Date preset for insights

        Returns:
            List of campaign dictionaries
        """
        fields = ['id', 'name', 'status', 'effective_status', 'daily_budget', 'lifetime_budget', 'objective']

        if include_insights:
            fields.append(f'insights.date_preset({date_preset}){{spend,impressions,clicks,actions,action_values,purchase_roas}}')

        params = {
            'fields': ','.join(fields),
            'limit': 100
        }

        if status_filter:
            params['filtering'] = json.dumps([{
                'field': 'effective_status',
                'operator': 'IN',
                'value': status_filter
            }])

        result = self._request(f"/{self.config.ad_account_id}/campaigns", params)

        return result.get('data', [])

    def get_adsets(
        self,
        campaign_id: Optional[str] = None,
        include_insights: bool = True,
        date_preset: str = 'last_7d'
    ) -> List[Dict]:
        """
        Fetch ad sets with optional insights.

        Args:
            campaign_id: Filter by campaign ID
            include_insights: Include insights data
            date_preset: Date preset for insights

        Returns:
            List of ad set dictionaries
        """
        fields = ['id', 'name', 'status', 'effective_status', 'daily_budget', 'campaign_id', 'targeting']

        if include_insights:
            fields.append(f'insights.date_preset({date_preset}){{spend,impressions,clicks,actions,action_values,ctr,cpc}}')

        params = {
            'fields': ','.join(fields),
            'limit': 100
        }

        if campaign_id:
            params['filtering'] = json.dumps([{
                'field': 'campaign.id',
                'operator': 'EQUAL',
                'value': campaign_id
            }])

        result = self._request(f"/{self.config.ad_account_id}/adsets", params)

        return result.get('data', [])

    def get_ads(
        self,
        adset_id: Optional[str] = None,
        include_insights: bool = True,
        date_preset: str = 'last_7d'
    ) -> List[Dict]:
        """Fetch ads with optional insights"""
        fields = ['id', 'name', 'status', 'effective_status', 'creative', 'adset_id']

        if include_insights:
            fields.append(f'insights.date_preset({date_preset}){{spend,impressions,clicks,ctr,cpc}}')

        params = {
            'fields': ','.join(fields),
            'limit': 100
        }

        if adset_id:
            params['filtering'] = json.dumps([{
                'field': 'adset.id',
                'operator': 'EQUAL',
                'value': adset_id
            }])

        result = self._request(f"/{self.config.ad_account_id}/ads", params)

        return result.get('data', [])

    def update_status(self, entity_id: str, status: str) -> Dict:
        """
        Update entity status (campaign, adset, or ad).

        Args:
            entity_id: The ID of the entity
            status: New status (ACTIVE, PAUSED)

        Returns:
            API response
        """
        return self._request(f"/{entity_id}", {'status': status}, method="POST")

    def update_budget(self, entity_id: str, budget_cents: int, budget_type: str = 'daily_budget') -> Dict:
        """
        Update entity budget.

        Args:
            entity_id: The ID of the entity
            budget_cents: Budget in cents
            budget_type: 'daily_budget' or 'lifetime_budget'

        Returns:
            API response
        """
        return self._request(f"/{entity_id}", {budget_type: budget_cents}, method="POST")

    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        params = {'fields': 'name,currency,account_status,business_name'}
        result = self._request(f"/{self.config.ad_account_id}", params)

        if 'error' not in result:
            return result
        return None
