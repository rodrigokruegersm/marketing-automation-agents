"""
Platform Adapters
Connectors for external platforms (Meta, Hyros, Leonardo.ai, Creatomate, etc.)
"""

from .meta_ads import MetaAdsAdapter
from .hyros import HyrosAdapter
from .leonardo import (
    LeonardoAdapter,
    LeonardoModel,
    AspectRatio,
    GeneratedImage
)
from .creatomate import (
    CreatomateAdapter,
    VideoFormat,
    AspectRatio as VideoAspectRatio,
    Resolution,
    RenderResult
)

__all__ = [
    'MetaAdsAdapter',
    'HyrosAdapter',
    'LeonardoAdapter',
    'LeonardoModel',
    'AspectRatio',
    'GeneratedImage',
    'CreatomateAdapter',
    'VideoFormat',
    'VideoAspectRatio',
    'Resolution',
    'RenderResult'
]
