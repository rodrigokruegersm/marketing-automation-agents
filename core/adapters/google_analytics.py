"""
Google Analytics 4 (GA4) Adapter
Connects to Google Analytics Data API for website metrics
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class GAMetric(Enum):
    """Available GA4 metrics"""
    SESSIONS = "sessions"
    USERS = "totalUsers"
    NEW_USERS = "newUsers"
    PAGEVIEWS = "screenPageViews"
    BOUNCE_RATE = "bounceRate"
    AVG_SESSION_DURATION = "averageSessionDuration"
    CONVERSIONS = "conversions"
    CONVERSION_RATE = "sessionConversionRate"
    REVENUE = "totalRevenue"
    TRANSACTIONS = "transactions"
    ECOMMERCE_PURCHASES = "ecommercePurchases"


class GADimension(Enum):
    """Available GA4 dimensions"""
    DATE = "date"
    SOURCE = "sessionSource"
    MEDIUM = "sessionMedium"
    CAMPAIGN = "sessionCampaignName"
    CHANNEL = "sessionDefaultChannelGroup"
    DEVICE = "deviceCategory"
    COUNTRY = "country"
    PAGE_PATH = "pagePath"
    LANDING_PAGE = "landingPage"


@dataclass
class GAReport:
    """Google Analytics report data"""
    sessions: int = 0
    users: int = 0
    new_users: int = 0
    pageviews: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversions: int = 0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    transactions: int = 0

    # Traffic sources
    organic_sessions: int = 0
    paid_sessions: int = 0
    direct_sessions: int = 0
    social_sessions: int = 0
    referral_sessions: int = 0

    # Device breakdown
    desktop_sessions: int = 0
    mobile_sessions: int = 0
    tablet_sessions: int = 0

    # Top pages
    top_pages: List[Dict] = None

    # Traffic by source
    traffic_sources: List[Dict] = None

    def __post_init__(self):
        if self.top_pages is None:
            self.top_pages = []
        if self.traffic_sources is None:
            self.traffic_sources = []


class GoogleAnalyticsAdapter:
    """
    Adapter for Google Analytics 4 (GA4) Data API

    Supports both:
    - Service Account authentication (for server-to-server)
    - OAuth2 access token (for user-authenticated requests)
    """

    BASE_URL = "https://analyticsdata.googleapis.com/v1beta"

    def __init__(
        self,
        property_id: str,
        access_token: Optional[str] = None,
        service_account_json: Optional[str] = None,
        credentials_json: Optional[str] = None
    ):
        """
        Initialize GA4 adapter

        Args:
            property_id: GA4 property ID (e.g., "517600570" or "properties/517600570")
            access_token: OAuth2 access token
            service_account_json: Path to service account JSON file
            credentials_json: Service account JSON as string (alternative to file)
        """
        # Ensure property_id is in correct format
        if property_id and not property_id.startswith("properties/"):
            self.property_id = f"properties/{property_id}"
        else:
            self.property_id = property_id

        self.access_token = access_token
        self.service_account_json = service_account_json
        self.credentials_json = credentials_json
        self._token = None
        self._token_expiry = None
        self._credentials = None

        # Parse credentials JSON if provided as string
        if credentials_json:
            try:
                self._credentials = json.loads(credentials_json) if isinstance(credentials_json, str) else credentials_json
            except json.JSONDecodeError:
                self._credentials = None

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        token = self._get_auth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _get_auth_token(self) -> str:
        """Get access token from service account or direct token"""
        if self.access_token:
            return self.access_token

        # Try to get token from service account credentials
        if self._credentials:
            return self._get_service_account_token()

        return ""

    def _get_service_account_token(self) -> str:
        """Get access token from service account using JWT"""
        try:
            import jwt
            import time

            if not self._credentials:
                return ""

            # Check if we have a valid cached token
            if self._token and self._token_expiry and time.time() < self._token_expiry:
                return self._token

            # Create JWT for service account
            now = int(time.time())
            claims = {
                "iss": self._credentials.get("client_email"),
                "sub": self._credentials.get("client_email"),
                "aud": "https://oauth2.googleapis.com/token",
                "iat": now,
                "exp": now + 3600,
                "scope": "https://www.googleapis.com/auth/analytics.readonly"
            }

            private_key = self._credentials.get("private_key", "")

            # Sign JWT
            signed_jwt = jwt.encode(
                claims,
                private_key,
                algorithm="RS256"
            )

            # Exchange JWT for access token
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                self._token = token_data.get("access_token")
                self._token_expiry = now + token_data.get("expires_in", 3600) - 60
                return self._token

            return ""

        except ImportError:
            # PyJWT not installed, return empty (will use mock data)
            return ""
        except Exception as e:
            print(f"GA Auth error: {e}")
            return ""

    def run_report(
        self,
        start_date: str,
        end_date: str,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        dimension_filter: Optional[Dict] = None,
        order_by: Optional[List[Dict]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Run a GA4 report

        Args:
            start_date: Start date (YYYY-MM-DD or "7daysAgo")
            end_date: End date (YYYY-MM-DD or "today")
            metrics: List of metric names
            dimensions: Optional list of dimension names
            dimension_filter: Optional dimension filter
            order_by: Optional ordering
            limit: Max rows to return

        Returns:
            Report data as dictionary
        """
        url = f"{self.BASE_URL}/{self.property_id}:runReport"

        request_body = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit
        }

        if dimensions:
            request_body["dimensions"] = [{"name": d} for d in dimensions]

        if dimension_filter:
            request_body["dimensionFilter"] = dimension_filter

        if order_by:
            request_body["orderBys"] = order_by

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=request_body,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}

    def get_overview(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today"
    ) -> GAReport:
        """
        Get overview metrics for the date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            GAReport with all metrics
        """
        metrics = [
            "sessions", "totalUsers", "newUsers", "screenPageViews",
            "bounceRate", "averageSessionDuration", "conversions",
            "sessionConversionRate", "totalRevenue", "transactions"
        ]

        report = self.run_report(start_date, end_date, metrics)

        if "error" in report:
            return GAReport()

        # Parse the response
        try:
            rows = report.get("rows", [])
            if rows:
                values = rows[0].get("metricValues", [])
                return GAReport(
                    sessions=int(float(values[0].get("value", 0))),
                    users=int(float(values[1].get("value", 0))),
                    new_users=int(float(values[2].get("value", 0))),
                    pageviews=int(float(values[3].get("value", 0))),
                    bounce_rate=float(values[4].get("value", 0)) * 100,
                    avg_session_duration=float(values[5].get("value", 0)),
                    conversions=int(float(values[6].get("value", 0))),
                    conversion_rate=float(values[7].get("value", 0)) * 100,
                    revenue=float(values[8].get("value", 0)),
                    transactions=int(float(values[9].get("value", 0)))
                )
        except (IndexError, KeyError, ValueError):
            pass

        return GAReport()

    def get_traffic_sources(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today",
        limit: int = 10
    ) -> List[Dict]:
        """
        Get traffic breakdown by source/medium

        Returns:
            List of traffic sources with sessions
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["sessions", "totalUsers", "conversions"],
            dimensions=["sessionSource", "sessionMedium"],
            order_by=[{"metric": {"metricName": "sessions"}, "desc": True}],
            limit=limit
        )

        if "error" in report:
            return []

        sources = []
        for row in report.get("rows", []):
            dims = row.get("dimensionValues", [])
            vals = row.get("metricValues", [])
            sources.append({
                "source": dims[0].get("value", "unknown"),
                "medium": dims[1].get("value", "unknown"),
                "sessions": int(float(vals[0].get("value", 0))),
                "users": int(float(vals[1].get("value", 0))),
                "conversions": int(float(vals[2].get("value", 0)))
            })

        return sources

    def get_channel_breakdown(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today"
    ) -> Dict[str, int]:
        """
        Get traffic breakdown by default channel group

        Returns:
            Dictionary with channel -> sessions
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["sessions"],
            dimensions=["sessionDefaultChannelGroup"]
        )

        if "error" in report:
            return {}

        channels = {}
        for row in report.get("rows", []):
            channel = row.get("dimensionValues", [{}])[0].get("value", "Other")
            sessions = int(float(row.get("metricValues", [{}])[0].get("value", 0)))
            channels[channel] = sessions

        return channels

    def get_device_breakdown(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today"
    ) -> Dict[str, int]:
        """
        Get traffic breakdown by device category

        Returns:
            Dictionary with device -> sessions
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["sessions"],
            dimensions=["deviceCategory"]
        )

        if "error" in report:
            return {}

        devices = {}
        for row in report.get("rows", []):
            device = row.get("dimensionValues", [{}])[0].get("value", "Other")
            sessions = int(float(row.get("metricValues", [{}])[0].get("value", 0)))
            devices[device] = sessions

        return devices

    def get_top_pages(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today",
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top pages by pageviews

        Returns:
            List of pages with metrics
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["screenPageViews", "averageSessionDuration", "bounceRate"],
            dimensions=["pagePath"],
            order_by=[{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            limit=limit
        )

        if "error" in report:
            return []

        pages = []
        for row in report.get("rows", []):
            path = row.get("dimensionValues", [{}])[0].get("value", "/")
            vals = row.get("metricValues", [])
            pages.append({
                "path": path,
                "pageviews": int(float(vals[0].get("value", 0))),
                "avg_time": float(vals[1].get("value", 0)),
                "bounce_rate": float(vals[2].get("value", 0)) * 100
            })

        return pages

    def get_landing_pages(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today",
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top landing pages with conversion metrics

        Returns:
            List of landing pages with metrics
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["sessions", "conversions", "sessionConversionRate", "bounceRate"],
            dimensions=["landingPage"],
            order_by=[{"metric": {"metricName": "sessions"}, "desc": True}],
            limit=limit
        )

        if "error" in report:
            return []

        pages = []
        for row in report.get("rows", []):
            path = row.get("dimensionValues", [{}])[0].get("value", "/")
            vals = row.get("metricValues", [])
            pages.append({
                "path": path,
                "sessions": int(float(vals[0].get("value", 0))),
                "conversions": int(float(vals[1].get("value", 0))),
                "conversion_rate": float(vals[2].get("value", 0)) * 100,
                "bounce_rate": float(vals[3].get("value", 0)) * 100
            })

        return pages

    def get_campaign_performance(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today",
        limit: int = 20
    ) -> List[Dict]:
        """
        Get performance by campaign (UTM campaign)

        Returns:
            List of campaigns with metrics
        """
        report = self.run_report(
            start_date,
            end_date,
            metrics=["sessions", "totalUsers", "conversions", "totalRevenue"],
            dimensions=["sessionCampaignName"],
            order_by=[{"metric": {"metricName": "sessions"}, "desc": True}],
            limit=limit
        )

        if "error" in report:
            return []

        campaigns = []
        for row in report.get("rows", []):
            campaign = row.get("dimensionValues", [{}])[0].get("value", "(not set)")
            vals = row.get("metricValues", [])
            campaigns.append({
                "campaign": campaign,
                "sessions": int(float(vals[0].get("value", 0))),
                "users": int(float(vals[1].get("value", 0))),
                "conversions": int(float(vals[2].get("value", 0))),
                "revenue": float(vals[3].get("value", 0))
            })

        return campaigns

    def get_full_report(
        self,
        start_date: str = "7daysAgo",
        end_date: str = "today"
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics report

        Returns:
            Dictionary with all analytics data
        """
        overview = self.get_overview(start_date, end_date)

        return {
            "overview": {
                "sessions": overview.sessions,
                "users": overview.users,
                "new_users": overview.new_users,
                "pageviews": overview.pageviews,
                "bounce_rate": overview.bounce_rate,
                "avg_session_duration": overview.avg_session_duration,
                "conversions": overview.conversions,
                "conversion_rate": overview.conversion_rate,
                "revenue": overview.revenue,
                "transactions": overview.transactions
            },
            "channels": self.get_channel_breakdown(start_date, end_date),
            "devices": self.get_device_breakdown(start_date, end_date),
            "traffic_sources": self.get_traffic_sources(start_date, end_date),
            "top_pages": self.get_top_pages(start_date, end_date),
            "landing_pages": self.get_landing_pages(start_date, end_date),
            "campaigns": self.get_campaign_performance(start_date, end_date)
        }


# Demo/Mock data for testing without actual GA connection
def get_mock_ga_data(days: int = 7) -> Dict[str, Any]:
    """
    Generate mock GA data for testing/demo purposes

    Args:
        days: Number of days of data

    Returns:
        Mock analytics data
    """
    import random

    base_sessions = 1500 if days == 7 else 650
    base_users = int(base_sessions * 0.7)

    return {
        "overview": {
            "sessions": base_sessions + random.randint(-100, 100),
            "users": base_users + random.randint(-50, 50),
            "new_users": int(base_users * 0.4) + random.randint(-20, 20),
            "pageviews": base_sessions * 3 + random.randint(-200, 200),
            "bounce_rate": 45.5 + random.uniform(-5, 5),
            "avg_session_duration": 125.5 + random.uniform(-20, 20),
            "conversions": int(base_sessions * 0.025) + random.randint(-5, 5),
            "conversion_rate": 2.5 + random.uniform(-0.5, 0.5),
            "revenue": base_sessions * 15 + random.uniform(-500, 500),
            "transactions": int(base_sessions * 0.02) + random.randint(-3, 3)
        },
        "channels": {
            "Paid Social": int(base_sessions * 0.45),
            "Organic Search": int(base_sessions * 0.20),
            "Direct": int(base_sessions * 0.15),
            "Referral": int(base_sessions * 0.10),
            "Organic Social": int(base_sessions * 0.07),
            "Email": int(base_sessions * 0.03)
        },
        "devices": {
            "mobile": int(base_sessions * 0.65),
            "desktop": int(base_sessions * 0.30),
            "tablet": int(base_sessions * 0.05)
        },
        "traffic_sources": [
            {"source": "facebook", "medium": "cpc", "sessions": int(base_sessions * 0.40), "users": int(base_users * 0.35), "conversions": int(base_sessions * 0.01)},
            {"source": "google", "medium": "organic", "sessions": int(base_sessions * 0.18), "users": int(base_users * 0.15), "conversions": int(base_sessions * 0.005)},
            {"source": "(direct)", "medium": "(none)", "sessions": int(base_sessions * 0.12), "users": int(base_users * 0.10), "conversions": int(base_sessions * 0.003)},
            {"source": "instagram", "medium": "cpc", "sessions": int(base_sessions * 0.08), "users": int(base_users * 0.07), "conversions": int(base_sessions * 0.002)},
            {"source": "google", "medium": "cpc", "sessions": int(base_sessions * 0.05), "users": int(base_users * 0.04), "conversions": int(base_sessions * 0.002)}
        ],
        "top_pages": [
            {"path": "/", "pageviews": int(base_sessions * 1.2), "avg_time": 45.2, "bounce_rate": 42.5},
            {"path": "/produto", "pageviews": int(base_sessions * 0.8), "avg_time": 120.5, "bounce_rate": 25.3},
            {"path": "/checkout", "pageviews": int(base_sessions * 0.15), "avg_time": 180.2, "bounce_rate": 15.8},
            {"path": "/sobre", "pageviews": int(base_sessions * 0.1), "avg_time": 60.3, "bounce_rate": 55.2}
        ],
        "landing_pages": [
            {"path": "/", "sessions": int(base_sessions * 0.5), "conversions": int(base_sessions * 0.01), "conversion_rate": 2.0, "bounce_rate": 45.0},
            {"path": "/lp/oferta", "sessions": int(base_sessions * 0.35), "conversions": int(base_sessions * 0.012), "conversion_rate": 3.4, "bounce_rate": 35.0},
            {"path": "/produto", "sessions": int(base_sessions * 0.15), "conversions": int(base_sessions * 0.003), "conversion_rate": 2.0, "bounce_rate": 40.0}
        ],
        "campaigns": [
            {"campaign": "[bsb] VSL Principal", "sessions": int(base_sessions * 0.35), "users": int(base_users * 0.30), "conversions": int(base_sessions * 0.01), "revenue": base_sessions * 5},
            {"campaign": "[bsb] Retargeting", "sessions": int(base_sessions * 0.15), "users": int(base_users * 0.12), "conversions": int(base_sessions * 0.008), "revenue": base_sessions * 4},
            {"campaign": "(not set)", "sessions": int(base_sessions * 0.30), "users": int(base_users * 0.25), "conversions": int(base_sessions * 0.005), "revenue": base_sessions * 3}
        ]
    }
