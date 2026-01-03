"""
Marketing Automation Agents
AI-powered agents for marketing automation tasks
"""

from .base import BaseAgent, AgentConfig, AgentResult
from .copy_forge import CopyForgeAgent
from .creative_lab import CreativeLabAgent
from .audience_builder import AudienceBuilderAgent
from .performance_optimizer import PerformanceOptimizerAgent
from .design_agent import DesignAgent
from .video_editor import VideoEditorAgent

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'AgentResult',
    'CopyForgeAgent',
    'CreativeLabAgent',
    'AudienceBuilderAgent',
    'PerformanceOptimizerAgent',
    'DesignAgent',
    'VideoEditorAgent',
]
