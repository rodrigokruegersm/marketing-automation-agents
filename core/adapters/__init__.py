"""
Platform Adapters
Connectors for external platforms (Meta, Hyros, Leonardo.ai, ElevenLabs, HeyGen, Creatomate, etc.)
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
from .elevenlabs import (
    ElevenLabsAdapter,
    VoiceModel,
    OutputFormat,
    Voice,
    GeneratedAudio
)
from .heygen import (
    HeyGenAdapter,
    VideoAspectRatio as HeyGenAspectRatio,
    VideoQuality,
    AvatarType,
    Avatar,
    VideoResult
)
from .google_analytics import (
    GoogleAnalyticsAdapter,
    GAMetric,
    GADimension,
    GAReport,
    get_mock_ga_data
)

__all__ = [
    # Meta & Attribution
    'MetaAdsAdapter',
    'HyrosAdapter',
    # Image Generation
    'LeonardoAdapter',
    'LeonardoModel',
    'AspectRatio',
    'GeneratedImage',
    # Video Templates
    'CreatomateAdapter',
    'VideoFormat',
    'VideoAspectRatio',
    'Resolution',
    'RenderResult',
    # Voice Cloning
    'ElevenLabsAdapter',
    'VoiceModel',
    'OutputFormat',
    'Voice',
    'GeneratedAudio',
    # Avatar Lip Sync
    'HeyGenAdapter',
    'HeyGenAspectRatio',
    'VideoQuality',
    'AvatarType',
    'Avatar',
    'VideoResult',
    # Analytics
    'GoogleAnalyticsAdapter',
    'GAMetric',
    'GADimension',
    'GAReport',
    'get_mock_ga_data'
]
