"""
Campaign Parser - Extracts funnel tags from campaign names

Naming Convention:
    {FUNNEL_TAG} - CAMPAIGN_TYPE - Description

Examples:
    {VSL_CHALLENGE} - COLD - Broad Interest
    {WEBINAR_LIVE} - RET - Viewers 50%
    {HIGH_TICKET} - COLD - Lookalike 1%
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class CampaignType(Enum):
    """Standard campaign types"""
    COLD = "cold"           # Cold traffic
    WARM = "warm"           # Warm/engaged audience
    RET = "retargeting"     # Retargeting
    LLA = "lookalike"       # Lookalike audiences
    CBO = "cbo"             # Campaign Budget Optimization
    ABO = "abo"             # Ad Set Budget Optimization
    TEST = "test"           # Testing campaigns
    SCALE = "scale"         # Scaling campaigns
    UNKNOWN = "unknown"


@dataclass
class ParsedCampaign:
    """Represents a parsed campaign with extracted metadata"""
    id: str
    name: str
    funnel_tag: str
    campaign_type: CampaignType
    description: str
    status: str
    effective_status: str
    daily_budget: float
    lifetime_budget: float
    objective: str
    metrics: Dict = field(default_factory=dict)
    raw_data: Dict = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.effective_status == "ACTIVE"

    @property
    def has_valid_tag(self) -> bool:
        return self.funnel_tag != "UNTAGGED"

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'funnel_tag': self.funnel_tag,
            'campaign_type': self.campaign_type.value,
            'description': self.description,
            'status': self.status,
            'effective_status': self.effective_status,
            'daily_budget': self.daily_budget,
            'is_active': self.is_active,
            'has_valid_tag': self.has_valid_tag,
            'metrics': self.metrics
        }


class CampaignParser:
    """
    Parser for extracting funnel tags and metadata from campaign names.

    Naming Convention:
        {FUNNEL_TAG} - CAMPAIGN_TYPE - Description

    The parser extracts:
        - Funnel tag (required, in curly braces)
        - Campaign type (optional, recognized keywords)
        - Description (remaining text)
    """

    # Regex pattern to extract {TAG} from campaign name
    TAG_PATTERN = re.compile(r'\{([^}]+)\}')

    # Recognized campaign type keywords
    TYPE_KEYWORDS = {
        'COLD': CampaignType.COLD,
        'WARM': CampaignType.WARM,
        'RET': CampaignType.RET,
        'RETARGETING': CampaignType.RET,
        'LLA': CampaignType.LLA,
        'LOOKALIKE': CampaignType.LLA,
        'CBO': CampaignType.CBO,
        'ABO': CampaignType.ABO,
        'TEST': CampaignType.TEST,
        'TESTE': CampaignType.TEST,
        'SCALE': CampaignType.SCALE,
        'ESCALA': CampaignType.SCALE,
    }

    def __init__(self):
        self.parsed_campaigns: List[ParsedCampaign] = []
        self.funnels: Dict[str, List[ParsedCampaign]] = {}
        self.untagged: List[ParsedCampaign] = []

    def parse_campaign_name(self, name: str) -> Tuple[str, CampaignType, str]:
        """
        Parse a campaign name to extract tag, type, and description.

        Args:
            name: Full campaign name

        Returns:
            Tuple of (funnel_tag, campaign_type, description)
        """
        # Extract funnel tag
        tag_match = self.TAG_PATTERN.search(name)
        funnel_tag = tag_match.group(1).upper() if tag_match else "UNTAGGED"

        # Remove tag from name for further parsing
        remaining = self.TAG_PATTERN.sub('', name).strip()

        # Split by common delimiters
        parts = re.split(r'\s*[-–|]\s*', remaining)
        parts = [p.strip() for p in parts if p.strip()]

        # Find campaign type
        campaign_type = CampaignType.UNKNOWN
        description_parts = []

        for part in parts:
            upper_part = part.upper()
            if upper_part in self.TYPE_KEYWORDS:
                campaign_type = self.TYPE_KEYWORDS[upper_part]
            else:
                description_parts.append(part)

        description = ' - '.join(description_parts) if description_parts else name

        return funnel_tag, campaign_type, description

    def parse_campaign(self, campaign_data: Dict) -> ParsedCampaign:
        """
        Parse a single campaign from API response.

        Args:
            campaign_data: Raw campaign data from Meta Ads API

        Returns:
            ParsedCampaign object
        """
        name = campaign_data.get('name', '')
        funnel_tag, campaign_type, description = self.parse_campaign_name(name)

        # Extract metrics if available
        metrics = {}
        insights = campaign_data.get('insights', {})
        if isinstance(insights, dict) and 'data' in insights:
            insights_data = insights['data'][0] if insights['data'] else {}
            metrics = {
                'spend': float(insights_data.get('spend', 0)),
                'impressions': int(insights_data.get('impressions', 0)),
                'clicks': int(insights_data.get('clicks', 0)),
                'ctr': float(insights_data.get('ctr', 0)),
                'cpc': float(insights_data.get('cpc', 0)),
            }

            # Extract purchase ROAS if available
            roas_data = insights_data.get('purchase_roas', [])
            if roas_data and isinstance(roas_data, list):
                metrics['roas'] = float(roas_data[0].get('value', 0))

            # Extract conversions
            actions = insights_data.get('actions', [])
            for action in actions:
                if action.get('action_type') == 'purchase':
                    metrics['purchases'] = float(action.get('value', 0))
                elif action.get('action_type') == 'lead':
                    metrics['leads'] = float(action.get('value', 0))

        # Calculate derived metrics
        if metrics.get('spend', 0) > 0 and metrics.get('purchases', 0) > 0:
            metrics['cpp'] = metrics['spend'] / metrics['purchases']

        parsed = ParsedCampaign(
            id=campaign_data.get('id', ''),
            name=name,
            funnel_tag=funnel_tag,
            campaign_type=campaign_type,
            description=description,
            status=campaign_data.get('status', 'UNKNOWN'),
            effective_status=campaign_data.get('effective_status', 'UNKNOWN'),
            daily_budget=float(campaign_data.get('daily_budget', 0)) / 100,
            lifetime_budget=float(campaign_data.get('lifetime_budget', 0)) / 100,
            objective=campaign_data.get('objective', ''),
            metrics=metrics,
            raw_data=campaign_data
        )

        return parsed

    def parse_campaigns(self, campaigns: List[Dict]) -> List[ParsedCampaign]:
        """
        Parse multiple campaigns and organize by funnel.

        Args:
            campaigns: List of campaign data from Meta Ads API

        Returns:
            List of ParsedCampaign objects
        """
        self.parsed_campaigns = []
        self.funnels = {}
        self.untagged = []

        for campaign_data in campaigns:
            parsed = self.parse_campaign(campaign_data)
            self.parsed_campaigns.append(parsed)

            # Organize by funnel
            if parsed.has_valid_tag:
                if parsed.funnel_tag not in self.funnels:
                    self.funnels[parsed.funnel_tag] = []
                self.funnels[parsed.funnel_tag].append(parsed)
            else:
                self.untagged.append(parsed)

        return self.parsed_campaigns

    def get_funnel_summary(self) -> Dict[str, Dict]:
        """
        Get aggregated metrics by funnel.

        Returns:
            Dict with funnel tag as key and aggregated metrics as value
        """
        summary = {}

        for tag, campaigns in self.funnels.items():
            active_campaigns = [c for c in campaigns if c.is_active]

            total_spend = sum(c.metrics.get('spend', 0) for c in campaigns)
            total_purchases = sum(c.metrics.get('purchases', 0) for c in campaigns)
            total_impressions = sum(c.metrics.get('impressions', 0) for c in campaigns)
            total_clicks = sum(c.metrics.get('clicks', 0) for c in campaigns)

            # Calculate averages
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_cpp = (total_spend / total_purchases) if total_purchases > 0 else 0

            # Get ROAS from campaigns that have it
            roas_values = [c.metrics.get('roas', 0) for c in campaigns if c.metrics.get('roas', 0) > 0]
            avg_roas = sum(roas_values) / len(roas_values) if roas_values else 0

            summary[tag] = {
                'funnel_tag': tag,
                'total_campaigns': len(campaigns),
                'active_campaigns': len(active_campaigns),
                'total_spend': total_spend,
                'total_purchases': total_purchases,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'avg_ctr': avg_ctr,
                'avg_cpp': avg_cpp,
                'avg_roas': avg_roas,
                'campaigns': [c.to_dict() for c in campaigns]
            }

        return summary

    def get_available_funnels(self) -> List[str]:
        """Get list of all detected funnel tags"""
        return list(self.funnels.keys())

    def get_campaigns_by_funnel(self, funnel_tag: str) -> List[ParsedCampaign]:
        """Get all campaigns for a specific funnel"""
        return self.funnels.get(funnel_tag.upper(), [])

    def get_campaigns_by_type(self, campaign_type: CampaignType) -> List[ParsedCampaign]:
        """Get all campaigns of a specific type"""
        return [c for c in self.parsed_campaigns if c.campaign_type == campaign_type]


# Utility functions for quick parsing
def extract_funnel_tag(campaign_name: str) -> str:
    """Quick function to extract funnel tag from campaign name"""
    match = re.search(r'\{([^}]+)\}', campaign_name)
    return match.group(1).upper() if match else "UNTAGGED"


def has_funnel_tag(campaign_name: str) -> bool:
    """Check if campaign name has a valid funnel tag"""
    return bool(re.search(r'\{[^}]+\}', campaign_name))
