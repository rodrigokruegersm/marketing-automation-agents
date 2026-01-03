"""
Platform Adapters
Connectors for external platforms (Meta, Hyros, etc.)
"""

from .meta_ads import MetaAdsAdapter
from .hyros import HyrosAdapter

__all__ = ['MetaAdsAdapter', 'HyrosAdapter']
