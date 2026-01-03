"""
Client Registry - Manages multi-client configuration
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Client:
    """Represents a client/account in the system"""
    id: str
    name: str
    slug: str
    status: str  # active, paused, churned
    meta_account_id: str
    meta_access_token: str
    google_account_id: Optional[str] = None
    hyrals_api_key: Optional[str] = None
    commission_rate: float = 0.20
    funnels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    config_path: Optional[Path] = None

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def data_dir(self) -> Path:
        if self.config_path:
            return self.config_path.parent / "data"
        return Path(f"clients/{self.slug}/data")

    @property
    def reports_dir(self) -> Path:
        if self.config_path:
            return self.config_path.parent / "reports"
        return Path(f"clients/{self.slug}/reports")

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status,
            'meta_account_id': self.meta_account_id,
            'commission_rate': self.commission_rate,
            'funnels': self.funnels,
            'is_active': self.is_active
        }


class ClientRegistry:
    """
    Manages client configurations and provides access to client data.

    Structure:
        clients/
            _registry.yaml          # Index of all clients
            {client-slug}/
                config.yaml         # Client configuration
                funnels/            # Funnel-specific configs
                data/               # Metrics and logs
                reports/            # Generated reports
    """

    def __init__(self, clients_dir: str = "clients"):
        self.clients_dir = Path(clients_dir)
        self.clients: Dict[str, Client] = {}
        self.registry_path = self.clients_dir / "_registry.yaml"
        self._load_registry()

    def _load_registry(self):
        """Load all client configurations"""
        self.clients = {}

        # First try to load from registry file
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                registry_data = yaml.safe_load(f) or {}
                for client_data in registry_data.get('clients', []):
                    client = self._load_client(client_data['slug'])
                    if client:
                        self.clients[client.slug] = client

        # Also scan for client folders
        if self.clients_dir.exists():
            for client_folder in self.clients_dir.iterdir():
                if client_folder.is_dir() and not client_folder.name.startswith('_'):
                    if client_folder.name not in self.clients:
                        client = self._load_client(client_folder.name)
                        if client:
                            self.clients[client.slug] = client

    def _load_client(self, slug: str) -> Optional[Client]:
        """Load a single client from config file"""
        config_path = self.clients_dir / slug / "config.yaml"

        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            client_config = config.get('client', {})

            # Get credentials from environment or config
            meta_token = os.getenv(
                f'{slug.upper().replace("-", "_")}_META_TOKEN',
                os.getenv('META_ACCESS_TOKEN', client_config.get('meta_access_token', ''))
            )
            meta_account = os.getenv(
                f'{slug.upper().replace("-", "_")}_META_ACCOUNT',
                os.getenv('META_AD_ACCOUNT_ID', client_config.get('meta_account_id', ''))
            )

            # Load funnels from config
            funnels = []
            funnels_config = config.get('funnels', [])
            if isinstance(funnels_config, list):
                funnels = [f.get('tag', f.get('name', '')) for f in funnels_config]
            elif isinstance(funnels_config, dict):
                funnels = list(funnels_config.keys())

            return Client(
                id=client_config.get('id', f'CLI_{slug.upper()[:3]}'),
                name=client_config.get('name', slug.replace('-', ' ').title()),
                slug=slug,
                status=client_config.get('status', 'active'),
                meta_account_id=meta_account,
                meta_access_token=meta_token,
                google_account_id=client_config.get('google_account_id'),
                hyrals_api_key=os.getenv(f'{slug.upper().replace("-", "_")}_HYRALS_KEY'),
                commission_rate=client_config.get('commission_rate', 0.20),
                funnels=funnels,
                config_path=config_path
            )
        except Exception as e:
            print(f"Error loading client {slug}: {e}")
            return None

    def get_client(self, slug: str) -> Optional[Client]:
        """Get a client by slug"""
        return self.clients.get(slug)

    def get_active_clients(self) -> List[Client]:
        """Get all active clients"""
        return [c for c in self.clients.values() if c.is_active]

    def get_all_clients(self) -> List[Client]:
        """Get all clients"""
        return list(self.clients.values())

    def get_client_by_meta_account(self, account_id: str) -> Optional[Client]:
        """Find client by Meta account ID"""
        for client in self.clients.values():
            if client.meta_account_id == account_id:
                return client
        return None

    def add_client(self, client: Client) -> bool:
        """Add a new client to registry"""
        if client.slug in self.clients:
            return False

        self.clients[client.slug] = client
        self._save_registry()
        return True

    def _save_registry(self):
        """Save registry index file"""
        registry_data = {
            'clients': [
                {
                    'slug': c.slug,
                    'name': c.name,
                    'status': c.status,
                    'meta_account_id': c.meta_account_id
                }
                for c in self.clients.values()
            ],
            'updated_at': datetime.now().isoformat()
        }

        self.clients_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            yaml.dump(registry_data, f, default_flow_style=False)

    def create_client_structure(self, slug: str, name: str, meta_account_id: str) -> Client:
        """Create folder structure for a new client"""
        client_dir = self.clients_dir / slug

        # Create directories
        (client_dir / "data").mkdir(parents=True, exist_ok=True)
        (client_dir / "reports").mkdir(parents=True, exist_ok=True)
        (client_dir / "funnels").mkdir(parents=True, exist_ok=True)
        (client_dir / "dashboards" / "streamlit").mkdir(parents=True, exist_ok=True)

        # Create config file
        config = {
            'client': {
                'id': f'CLI_{slug.upper()[:3]}{len(self.clients) + 1:03d}',
                'name': name,
                'slug': slug,
                'status': 'active',
                'meta_account_id': meta_account_id,
                'commission_rate': 0.20,
                'onboarding_date': datetime.now().strftime('%Y-%m-%d')
            },
            'funnels': [],
            'metrics_targets': {
                'roas_target': 2.0,
                'roas_min': 1.5,
                'cpp_max': 25.0,
                'ctr_min': 1.5
            }
        }

        config_path = client_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        # Reload and return new client
        client = self._load_client(slug)
        if client:
            self.clients[slug] = client
            self._save_registry()
        return client

    def list_clients_summary(self) -> List[Dict]:
        """Get summary of all clients for UI display"""
        return [
            {
                'slug': c.slug,
                'name': c.name,
                'status': c.status,
                'funnels_count': len(c.funnels),
                'is_active': c.is_active
            }
            for c in self.clients.values()
        ]
