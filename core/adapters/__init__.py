"""
Platform Adapters
Connectors for external platforms (Meta, Hyros, Leonardo.ai, etc.)
"""

from .meta_ads import MetaAdsAdapter
from .hyros import HyrosAdapter
from .leonardo import (
    LeonardoAdapter,
    LeonardoModel,
    AspectRatio,
    GeneratedImage
)

__all__ = [
    'MetaAdsAdapter',
    'HyrosAdapter',
    'LeonardoAdapter',
    'LeonardoModel',
    'AspectRatio',
    'GeneratedImage'
]
