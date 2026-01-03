"""
Data Aggregator - Aggregates metrics by client, funnel, and campaign

Includes product-aware analysis for accurate CPP optimization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

from .campaign_parser import CampaignParser, ParsedCampaign
from .client_registry import Client
from .funnel_registry import Funnel, FunnelRegistry
from .product_registry import ProductRegistry, FunnelProduct


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a group of campaigns"""
    spend: float = 0.0
    revenue: float = 0.0
    profit: float = 0.0
    impressions: int = 0
    reach: int = 0
    clicks: int = 0
    purchases: int = 0
    leads: int = 0

    # Calculated metrics
    roas: float = 0.0
    cpp: float = 0.0
    cpl: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    frequency: float = 0.0

    # Counts
    total_campaigns: int = 0
    active_campaigns: int = 0

    # Product-aware metrics (set when product data is available)
    product_price: float = 0.0
    breakeven_cpp: float = 0.0
    target_cpp: float = 0.0
    cpp_margin: float = 0.0  # How much room before hitting breakeven
    cpp_status: str = ""  # excellent, good, warning, critical

    def calculate_derived(self):
        """Calculate derived metrics"""
        if self.spend > 0:
            self.roas = self.revenue / self.spend if self.revenue > 0 else 0
            self.cpp = self.spend / self.purchases if self.purchases > 0 else 0
            self.cpl = self.spend / self.leads if self.leads > 0 else 0
            self.cpc = self.spend / self.clicks if self.clicks > 0 else 0
            self.cpm = (self.spend / self.impressions * 1000) if self.impressions > 0 else 0

        if self.impressions > 0:
            self.ctr = (self.clicks / self.impressions * 100)
            if self.reach > 0:
                self.frequency = self.impressions / self.reach

        self.profit = self.revenue - self.spend

        # Calculate CPP margin if breakeven is set
        if self.breakeven_cpp > 0 and self.cpp > 0:
            self.cpp_margin = self.breakeven_cpp - self.cpp

    def apply_product_thresholds(self, product: Optional[FunnelProduct]):
        """Apply product-based thresholds for CPP analysis"""
        if not product:
            return

        self.product_price = product.price
        self.breakeven_cpp = product.breakeven_cpp or product.net_revenue_per_sale
        self.target_cpp = product.target_cpp or (self.breakeven_cpp / product.target_roas)

        # Evaluate CPP status
        if self.cpp > 0:
            self.cpp_status = product.evaluate_cpp(self.cpp)
            self.cpp_margin = self.breakeven_cpp - self.cpp

    def to_dict(self) -> Dict:
        return {
            'spend': self.spend,
            'revenue': self.revenue,
            'profit': self.profit,
            'impressions': self.impressions,
            'reach': self.reach,
            'clicks': self.clicks,
            'purchases': self.purchases,
            'leads': self.leads,
            'roas': self.roas,
            'cpp': self.cpp,
            'cpl': self.cpl,
            'ctr': self.ctr,
            'cpc': self.cpc,
            'cpm': self.cpm,
            'frequency': self.frequency,
            'total_campaigns': self.total_campaigns,
            'active_campaigns': self.active_campaigns,
            # Product-aware metrics
            'product_price': self.product_price,
            'breakeven_cpp': self.breakeven_cpp,
            'target_cpp': self.target_cpp,
            'cpp_margin': self.cpp_margin,
            'cpp_status': self.cpp_status
        }


@dataclass
class FunnelData:
    """Aggregated data for a specific funnel"""
    funnel_tag: str
    funnel_name: str
    funnel_type: str
    client_slug: str
    metrics: AggregatedMetrics
    campaigns: List[ParsedCampaign] = field(default_factory=list)
    status: str = "healthy"  # healthy, warning, critical
    alerts: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

    # Product data (when available)
    product: Optional[FunnelProduct] = None
    product_name: str = ""
    product_price: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'funnel_tag': self.funnel_tag,
            'funnel_name': self.funnel_name,
            'funnel_type': self.funnel_type,
            'client_slug': self.client_slug,
            'metrics': self.metrics.to_dict(),
            'campaigns_count': len(self.campaigns),
            'status': self.status,
            'alerts': self.alerts,
            'opportunities': self.opportunities,
            'product_name': self.product_name,
            'product_price': self.product_price
        }


@dataclass
class ClientData:
    """Aggregated data for a client"""
    client: Client
    metrics: AggregatedMetrics
    funnels: Dict[str, FunnelData] = field(default_factory=dict)
    all_campaigns: List[ParsedCampaign] = field(default_factory=list)
    untagged_campaigns: List[ParsedCampaign] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'client': self.client.to_dict(),
            'metrics': self.metrics.to_dict(),
            'funnels': {k: v.to_dict() for k, v in self.funnels.items()},
            'total_campaigns': len(self.all_campaigns),
            'untagged_count': len(self.untagged_campaigns),
            'updated_at': self.updated_at.isoformat()
        }


class DataAggregator:
    """
    Aggregates campaign data by client and funnel.

    Includes product-aware CPP analysis for accurate optimization.

    Usage:
        aggregator = DataAggregator()

        # Basic aggregation
        client_data = aggregator.aggregate_client(client, campaigns_data)

        # With product data for accurate CPP analysis
        product_registry = ProductRegistry()
        product_registry.load_client_products("brez-scales")
        client_data = aggregator.aggregate_client(
            client, campaigns_data,
            product_registry=product_registry
        )
    """

    def __init__(
        self,
        funnel_registry: Optional[FunnelRegistry] = None,
        product_registry: Optional[ProductRegistry] = None
    ):
        self.parser = CampaignParser()
        self.funnel_registry = funnel_registry or FunnelRegistry()
        self.product_registry = product_registry

    def aggregate_campaigns(self, campaigns: List[ParsedCampaign]) -> AggregatedMetrics:
        """Aggregate metrics from a list of campaigns"""
        metrics = AggregatedMetrics()

        for campaign in campaigns:
            m = campaign.metrics
            metrics.spend += m.get('spend', 0)
            metrics.revenue += m.get('revenue', 0)
            metrics.impressions += m.get('impressions', 0)
            metrics.reach += m.get('reach', 0)
            metrics.clicks += m.get('clicks', 0)
            metrics.purchases += m.get('purchases', 0)
            metrics.leads += m.get('leads', 0)
            metrics.total_campaigns += 1
            if campaign.is_active:
                metrics.active_campaigns += 1

        metrics.calculate_derived()
        return metrics

    def aggregate_client(
        self,
        client: Client,
        raw_campaigns: List[Dict],
        product_registry: Optional[ProductRegistry] = None
    ) -> ClientData:
        """
        Aggregate all data for a client.

        Args:
            client: Client object
            raw_campaigns: Raw campaign data from Meta Ads API
            product_registry: Optional ProductRegistry for CPP analysis

        Returns:
            ClientData with aggregated metrics by funnel
        """
        # Use provided registry or instance default
        products = product_registry or self.product_registry

        # Parse all campaigns
        parsed_campaigns = self.parser.parse_campaigns(raw_campaigns)

        # Load funnel configurations
        client_funnels = self.funnel_registry.load_client_funnels(client.slug)

        # Aggregate by funnel
        funnels_data: Dict[str, FunnelData] = {}

        for tag, campaigns in self.parser.funnels.items():
            # Get or create funnel config
            funnel_config = client_funnels.get(tag)
            if not funnel_config:
                funnel_config = self.funnel_registry.get_or_create_funnel(client.slug, tag)

            # Aggregate metrics
            metrics = self.aggregate_campaigns(campaigns)

            # Get product data for this funnel
            funnel_product = None
            if products:
                funnel_product = products.get_product_for_funnel(tag)
                if funnel_product:
                    metrics.apply_product_thresholds(funnel_product)

            # Determine status and generate alerts (with product awareness)
            status, alerts, opportunities = self._analyze_funnel_health(
                funnel_config, metrics, campaigns, funnel_product
            )

            funnels_data[tag] = FunnelData(
                funnel_tag=tag,
                funnel_name=funnel_config.name,
                funnel_type=funnel_config.type.value,
                client_slug=client.slug,
                metrics=metrics,
                campaigns=campaigns,
                status=status,
                alerts=alerts,
                opportunities=opportunities,
                product=funnel_product,
                product_name=funnel_product.name if funnel_product else "",
                product_price=funnel_product.price if funnel_product else 0.0
            )

        # Aggregate total metrics
        total_metrics = self.aggregate_campaigns(parsed_campaigns)

        return ClientData(
            client=client,
            metrics=total_metrics,
            funnels=funnels_data,
            all_campaigns=parsed_campaigns,
            untagged_campaigns=self.parser.untagged,
            updated_at=datetime.now()
        )

    def _analyze_funnel_health(
        self,
        funnel: Funnel,
        metrics: AggregatedMetrics,
        campaigns: List[ParsedCampaign],
        product: Optional[FunnelProduct] = None
    ) -> tuple:
        """
        Analyze funnel health and generate alerts/opportunities.

        Uses product data for accurate CPP analysis when available.

        Returns:
            Tuple of (status, alerts, opportunities)
        """
        alerts = []
        opportunities = []
        has_critical = False
        has_warning = False

        # Check ROAS
        if metrics.roas > 0:
            roas_status = funnel.evaluate_metric('roas', metrics.roas)
            if roas_status == 'critical':
                alerts.append(f"ROAS critico: {metrics.roas:.2f}x - Pausar campanhas de baixo desempenho")
                has_critical = True
            elif roas_status == 'warning':
                alerts.append(f"ROAS baixo: {metrics.roas:.2f}x - Revisar targeting e criativos")
                has_warning = True
            elif roas_status == 'excellent':
                opportunities.append(f"ROAS excelente: {metrics.roas:.2f}x - Oportunidade de escala")

        # Check CPP (with product-aware analysis)
        if metrics.cpp > 0:
            if product and product.breakeven_cpp:
                # Use product-based CPP analysis
                cpp_status = product.evaluate_cpp(metrics.cpp)
                breakeven = product.breakeven_cpp
                target = product.target_cpp or breakeven / 2

                if cpp_status == 'critical':
                    alerts.append(
                        f"CPP ACIMA DO BREAKEVEN: ${metrics.cpp:.2f} "
                        f"(max: ${breakeven:.2f}) - PAUSAR URGENTE"
                    )
                    has_critical = True
                elif cpp_status == 'warning':
                    margin = breakeven - metrics.cpp
                    alerts.append(
                        f"CPP proximo do limite: ${metrics.cpp:.2f} "
                        f"(margem: ${margin:.2f} ate breakeven)"
                    )
                    has_warning = True
                elif cpp_status == 'excellent':
                    margin = target - metrics.cpp
                    opportunities.append(
                        f"CPP excelente: ${metrics.cpp:.2f} "
                        f"(${margin:.2f} abaixo do target) - Escalar!"
                    )
                elif cpp_status == 'good':
                    opportunities.append(
                        f"CPP saudavel: ${metrics.cpp:.2f} "
                        f"(target: ${target:.2f}) - Margem para escala"
                    )
            else:
                # Fallback to funnel-based thresholds
                cpp_status = funnel.evaluate_metric('cpp', metrics.cpp)
                if cpp_status == 'critical':
                    alerts.append(f"CPP muito alto: ${metrics.cpp:.2f} - Otimizar urgente")
                    has_critical = True
                elif cpp_status == 'warning':
                    alerts.append(f"CPP alto: ${metrics.cpp:.2f} - Monitorar")
                    has_warning = True
                elif cpp_status == 'excellent':
                    opportunities.append(f"CPP excelente: ${metrics.cpp:.2f} - Escalar campanhas eficientes")

        # Check frequency
        if metrics.frequency > 0:
            freq_status = funnel.evaluate_metric('frequency', metrics.frequency)
            if freq_status == 'critical':
                alerts.append(f"Frequencia critica: {metrics.frequency:.2f} - Audiencia saturada")
                has_critical = True
            elif freq_status == 'warning':
                alerts.append(f"Frequencia alta: {metrics.frequency:.2f} - Preparar novos criativos")
                has_warning = True

        # Check CTR
        if metrics.ctr > 0:
            ctr_status = funnel.evaluate_metric('ctr', metrics.ctr)
            if ctr_status == 'critical':
                alerts.append(f"CTR baixo: {metrics.ctr:.2f}% - Revisar criativos urgente")
                has_warning = True
            elif ctr_status == 'excellent':
                opportunities.append(f"CTR forte: {metrics.ctr:.2f}% - Duplicar para novos publicos")

        # Product-specific insights
        if product and metrics.purchases > 0:
            estimated_revenue = metrics.purchases * product.price
            actual_profit = estimated_revenue - metrics.spend
            if actual_profit > 0:
                margin_percent = (actual_profit / estimated_revenue) * 100
                if margin_percent >= 50:
                    opportunities.append(
                        f"Margem saudavel: {margin_percent:.0f}% "
                        f"(${actual_profit:,.0f} lucro estimado)"
                    )

        # Determine overall status
        if has_critical:
            status = "critical"
        elif has_warning:
            status = "warning"
        else:
            status = "healthy"

        return status, alerts, opportunities

    def get_funnel_comparison(self, client_data: ClientData) -> List[Dict]:
        """
        Get comparison data for all funnels in a client.

        Returns list sorted by ROAS descending.
        """
        comparison = []

        for tag, funnel_data in client_data.funnels.items():
            comparison.append({
                'funnel': tag,
                'name': funnel_data.funnel_name,
                'type': funnel_data.funnel_type,
                'status': funnel_data.status,
                'spend': funnel_data.metrics.spend,
                'revenue': funnel_data.metrics.revenue,
                'roas': funnel_data.metrics.roas,
                'cpp': funnel_data.metrics.cpp,
                'purchases': funnel_data.metrics.purchases,
                'campaigns': funnel_data.metrics.total_campaigns,
                'active': funnel_data.metrics.active_campaigns
            })

        # Sort by ROAS descending
        comparison.sort(key=lambda x: x['roas'], reverse=True)
        return comparison

    def get_alerts_summary(self, client_data: ClientData) -> Dict:
        """Get summary of all alerts across funnels"""
        all_alerts = []
        all_opportunities = []
        status_counts = {'healthy': 0, 'warning': 0, 'critical': 0}

        for funnel_data in client_data.funnels.values():
            for alert in funnel_data.alerts:
                all_alerts.append({
                    'funnel': funnel_data.funnel_tag,
                    'message': alert,
                    'status': funnel_data.status
                })
            for opp in funnel_data.opportunities:
                all_opportunities.append({
                    'funnel': funnel_data.funnel_tag,
                    'message': opp
                })
            status_counts[funnel_data.status] += 1

        # Sort alerts by severity
        severity_order = {'critical': 0, 'warning': 1, 'healthy': 2}
        all_alerts.sort(key=lambda x: severity_order.get(x['status'], 3))

        return {
            'alerts': all_alerts,
            'opportunities': all_opportunities,
            'status_counts': status_counts,
            'overall_status': 'critical' if status_counts['critical'] > 0 else (
                'warning' if status_counts['warning'] > 0 else 'healthy'
            )
        }
