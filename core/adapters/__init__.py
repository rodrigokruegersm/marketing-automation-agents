"""
Platform Adapters
Connectors for external platforms (Meta, Hyros, Freepik, etc.)
"""

from .meta_ads import MetaAdsAdapter
from .hyros import HyrosAdapter
from .freepik import (
    FreepikAdapter,
    FreepikModel,
    FreepikEngine,
    AspectRatio,
    GeneratedImage
)

__all__ = [
    'MetaAdsAdapter',
    'HyrosAdapter',
    'FreepikAdapter',
    'FreepikModel',
    'FreepikEngine',
    'AspectRatio',
    'GeneratedImage'
]
