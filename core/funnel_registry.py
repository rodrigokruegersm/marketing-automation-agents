"""
Funnel Registry - Manages funnel types and configurations
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class FunnelType(Enum):
    """Standard funnel types with default KPI targets"""
    VSL_CHALLENGE = "vsl_challenge"
    WEBINAR_LIVE = "webinar_live"
    WEBINAR_EVERGREEN = "webinar_evergreen"
    HIGH_TICKET = "high_ticket"
    LOW_TICKET = "low_ticket"
    LEAD_GEN = "lead_gen"
    ECOMMERCE = "ecommerce"
    APP_INSTALL = "app_install"
    CUSTOM = "custom"


# Default KPI targets by funnel type
DEFAULT_THRESHOLDS = {
    FunnelType.VSL_CHALLENGE: {
        'roas_excellent': 3.0,
        'roas_good': 2.5,
        'roas_warning': 2.0,
        'roas_critical': 1.5,
        'cpp_excellent': 15,
        'cpp_good': 20,
        'cpp_warning': 30,
        'cpp_critical': 40,
        'ctr_min': 1.5,
        'frequency_max': 2.5,
        'checkout_rate_min': 5,
        'close_rate_min': 50
    },
    FunnelType.WEBINAR_LIVE: {
        'cpl_excellent': 10,
        'cpl_good': 15,
        'cpl_warning': 25,
        'cpl_critical': 35,
        'show_rate_min': 30,
        'close_rate_min': 5,
        'ctr_min': 1.0,
        'frequency_max': 3.0
    },
    FunnelType.HIGH_TICKET: {
        'roas_excellent': 5.0,
        'roas_good': 3.5,
        'roas_warning': 2.5,
        'roas_critical': 1.5,
        'cac_max': 500,
        'ltv_min': 2500,
        'call_book_rate_min': 10,
        'call_show_rate_min': 70,
        'close_rate_min': 20
    },
    FunnelType.LOW_TICKET: {
        'roas_excellent': 4.0,
        'roas_good': 3.0,
        'roas_warning': 2.0,
        'roas_critical': 1.2,
        'aov_min': 47,
        'frequency_max': 3.5,
        'ctr_min': 2.0
    },
    FunnelType.LEAD_GEN: {
        'cpl_excellent': 5,
        'cpl_good': 10,
        'cpl_warning': 20,
        'cpl_critical': 30,
        'lead_quality_min': 60,
        'ctr_min': 1.5,
        'form_completion_rate_min': 30
    },
    FunnelType.ECOMMERCE: {
        'roas_excellent': 5.0,
        'roas_good': 3.5,
        'roas_warning': 2.5,
        'roas_critical': 1.5,
        'aov_min': 50,
        'cart_abandon_rate_max': 70,
        'frequency_max': 4.0
    }
}


@dataclass
class Funnel:
    """Represents a funnel configuration"""
    id: str
    name: str
    tag: str  # Tag used in campaign names {TAG}
    type: FunnelType
    client_id: str
    thresholds: Dict = field(default_factory=dict)
    description: str = ""
    is_active: bool = True

    def __post_init__(self):
        # Apply default thresholds if not provided
        if not self.thresholds:
            self.thresholds = DEFAULT_THRESHOLDS.get(self.type, {}).copy()

    def get_threshold(self, metric: str, level: str = 'good') -> Optional[float]:
        """Get threshold value for a metric"""
        key = f'{metric}_{level}'
        return self.thresholds.get(key)

    def evaluate_metric(self, metric: str, value: float) -> str:
        """
        Evaluate a metric value against thresholds.

        Returns: 'excellent', 'good', 'warning', 'critical', or 'unknown'
        """
        excellent = self.thresholds.get(f'{metric}_excellent')
        good = self.thresholds.get(f'{metric}_good')
        warning = self.thresholds.get(f'{metric}_warning')
        critical = self.thresholds.get(f'{metric}_critical')

        # Handle metrics where higher is better (ROAS, CTR, rates)
        if metric in ['roas', 'ctr', 'close_rate', 'show_rate', 'checkout_rate']:
            if excellent and value >= excellent:
                return 'excellent'
            if good and value >= good:
                return 'good'
            if warning and value >= warning:
                return 'warning'
            if critical and value < critical:
                return 'critical'
            return 'warning'

        # Handle metrics where lower is better (CPL, CPP, CAC, frequency)
        if metric in ['cpl', 'cpp', 'cac', 'frequency', 'cart_abandon_rate']:
            if excellent and value <= excellent:
                return 'excellent'
            if good and value <= good:
                return 'good'
            if warning and value <= warning:
                return 'warning'
            if critical and value > critical:
                return 'critical'
            return 'warning'

        return 'unknown'

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'type': self.type.value,
            'client_id': self.client_id,
            'thresholds': self.thresholds,
            'description': self.description,
            'is_active': self.is_active
        }


class FunnelRegistry:
    """
    Manages funnel configurations per client.

    Structure:
        clients/{client}/funnels/
            {funnel_tag}.yaml
    """

    def __init__(self, clients_dir: str = "clients"):
        self.clients_dir = Path(clients_dir)
        self.funnels: Dict[str, Dict[str, Funnel]] = {}  # {client_slug: {tag: Funnel}}

    def load_client_funnels(self, client_slug: str) -> Dict[str, Funnel]:
        """Load all funnels for a client"""
        if client_slug in self.funnels:
            return self.funnels[client_slug]

        self.funnels[client_slug] = {}
        funnels_dir = self.clients_dir / client_slug / "funnels"

        if funnels_dir.exists():
            for funnel_file in funnels_dir.glob("*.yaml"):
                try:
                    with open(funnel_file, 'r') as f:
                        config = yaml.safe_load(f)

                    funnel = Funnel(
                        id=config.get('id', funnel_file.stem.upper()),
                        name=config.get('name', funnel_file.stem.replace('_', ' ').title()),
                        tag=config.get('tag', funnel_file.stem.upper()),
                        type=FunnelType(config.get('type', 'custom')),
                        client_id=client_slug,
                        thresholds=config.get('thresholds', {}),
                        description=config.get('description', ''),
                        is_active=config.get('is_active', True)
                    )
                    self.funnels[client_slug][funnel.tag] = funnel
                except Exception as e:
                    print(f"Error loading funnel {funnel_file}: {e}")

        # Also load from client config.yaml if funnels are defined there
        client_config = self.clients_dir / client_slug / "config.yaml"
        if client_config.exists():
            try:
                with open(client_config, 'r') as f:
                    config = yaml.safe_load(f)

                for funnel_config in config.get('funnels', []):
                    if isinstance(funnel_config, dict):
                        tag = funnel_config.get('tag', '').upper()
                        if tag and tag not in self.funnels[client_slug]:
                            funnel = Funnel(
                                id=funnel_config.get('id', f'FUN_{tag[:3]}'),
                                name=funnel_config.get('name', tag.replace('_', ' ').title()),
                                tag=tag,
                                type=FunnelType(funnel_config.get('type', 'custom')),
                                client_id=client_slug,
                                thresholds=funnel_config.get('thresholds', {}),
                                description=funnel_config.get('description', ''),
                                is_active=funnel_config.get('is_active', True)
                            )
                            self.funnels[client_slug][tag] = funnel
            except Exception as e:
                print(f"Error loading funnels from client config: {e}")

        return self.funnels[client_slug]

    def get_funnel(self, client_slug: str, tag: str) -> Optional[Funnel]:
        """Get a specific funnel by client and tag"""
        if client_slug not in self.funnels:
            self.load_client_funnels(client_slug)
        return self.funnels.get(client_slug, {}).get(tag.upper())

    def get_or_create_funnel(self, client_slug: str, tag: str, funnel_type: FunnelType = FunnelType.CUSTOM) -> Funnel:
        """Get existing funnel or create a new one with defaults"""
        funnel = self.get_funnel(client_slug, tag)
        if funnel:
            return funnel

        # Create new funnel with defaults
        funnel = Funnel(
            id=f'FUN_{tag[:6]}',
            name=tag.replace('_', ' ').title(),
            tag=tag.upper(),
            type=funnel_type,
            client_id=client_slug
        )

        if client_slug not in self.funnels:
            self.funnels[client_slug] = {}
        self.funnels[client_slug][tag.upper()] = funnel

        return funnel

    def create_funnel(self, client_slug: str, name: str, tag: str, funnel_type: FunnelType,
                     thresholds: Dict = None, description: str = "") -> Funnel:
        """Create and save a new funnel"""
        funnel = Funnel(
            id=f'FUN_{tag[:6]}_{len(self.funnels.get(client_slug, {})) + 1:03d}',
            name=name,
            tag=tag.upper(),
            type=funnel_type,
            client_id=client_slug,
            thresholds=thresholds or {},
            description=description
        )

        # Save to file
        funnels_dir = self.clients_dir / client_slug / "funnels"
        funnels_dir.mkdir(parents=True, exist_ok=True)

        funnel_file = funnels_dir / f"{tag.lower()}.yaml"
        with open(funnel_file, 'w') as f:
            yaml.dump(funnel.to_dict(), f, default_flow_style=False)

        # Add to registry
        if client_slug not in self.funnels:
            self.funnels[client_slug] = {}
        self.funnels[client_slug][tag.upper()] = funnel

        return funnel

    def list_funnels(self, client_slug: str) -> List[Dict]:
        """List all funnels for a client"""
        if client_slug not in self.funnels:
            self.load_client_funnels(client_slug)

        return [f.to_dict() for f in self.funnels.get(client_slug, {}).values()]

    def get_funnel_types(self) -> List[str]:
        """Get all available funnel types"""
        return [ft.value for ft in FunnelType]
