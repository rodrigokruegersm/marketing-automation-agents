"""
Video Editor Agent
AI-powered video ad generation using Creatomate API

Creates professional video ads for Meta, TikTok, YouTube, and display campaigns
with support for templates, dynamic content, and bulk generation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

from ..base import BaseAgent, AgentConfig, AgentResult

try:
    from core.adapters.creatomate import (
        CreatomateAdapter,
        VideoFormat,
        AspectRatio,
        Resolution,
        RenderResult
    )
    CREATOMATE_AVAILABLE = True
except ImportError:
    CREATOMATE_AVAILABLE = False


@dataclass
class VideoAd:
    """Generated video ad"""
    name: str
    render_id: str
    status: str
    format: str
    template_id: str
    url: Optional[str] = None
    duration: float = 0.0
    modifications: Dict[str, Any] = None

    def __post_init__(self):
        if self.modifications is None:
            self.modifications = {}


class VideoEditorAgent(BaseAgent):
    """
    AI Agent for generating video ads using Creatomate API.

    Capabilities:
    - Render videos from pre-made templates
    - Insert dynamic text, images, and videos
    - Generate video ad variations
    - Bulk video generation for A/B testing
    - Multiple formats (Feed, Story, Reels, TikTok)

    Actions:
    - render_video: Render a single video from template
    - render_ad_set: Generate complete ad set (multiple formats)
    - generate_variations: Generate multiple variations of same ad
    - bulk_render: Render multiple videos with different data
    - create_text_video: Create simple text-based video

    Usage:
        agent = VideoEditorAgent()
        result = agent.run({
            'action': 'render_video',
            'template_id': 'your-template-id',
            'modifications': {
                'Headline': 'Your Ad Headline',
                'CTA': 'Shop Now',
                'Video': 'https://example.com/product.mp4'
            }
        })
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.creatomate: Optional[CreatomateAdapter] = None
        self._init_creatomate()

    def _init_creatomate(self):
        """Initialize Creatomate adapter if API key available"""
        if CREATOMATE_AVAILABLE and os.getenv("CREATOMATE_API_KEY"):
            try:
                self.creatomate = CreatomateAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize Creatomate: {e}")

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="VideoEditorAgent",
            description="AI-powered video ad generation with Creatomate",
            version="1.0.0",
            model="creatomate",
            temperature=0.5,
            settings={
                'supported_actions': [
                    'render_video',
                    'render_ad_set',
                    'generate_variations',
                    'bulk_render',
                    'create_text_video',
                    'list_templates'
                ],
                'formats': {
                    'feed': {'width': 1080, 'height': 1080, 'ratio': '1:1'},
                    'story': {'width': 1080, 'height': 1920, 'ratio': '9:16'},
                    'reels': {'width': 1080, 'height': 1920, 'ratio': '9:16'},
                    'tiktok': {'width': 1080, 'height': 1920, 'ratio': '9:16'},
                    'youtube': {'width': 1920, 'height': 1080, 'ratio': '16:9'},
                    'display': {'width': 1920, 'height': 1080, 'ratio': '16:9'}
                },
                'default_templates': {
                    # These would be your saved templates in Creatomate
                    'product_showcase': None,
                    'testimonial': None,
                    'promo_offer': None,
                    'brand_awareness': None
                }
            }
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute video editor action.

        Args:
            context: Dictionary with:
                - action: Action to perform
                - template_id: Creatomate template ID
                - modifications: Dict of element names and values
                - format: Output format (mp4, gif)
                - variations: List of modification sets for variations
                - data_list: List of modification dicts for bulk render

        Returns:
            AgentResult with rendered video data
        """
        action = context.get('action', 'render_video')

        if not CREATOMATE_AVAILABLE:
            return AgentResult(
                success=False,
                data=None,
                message="Creatomate adapter not available. Install with: pip install requests"
            )

        if not self.creatomate:
            return AgentResult(
                success=False,
                data=None,
                message="CREATOMATE_API_KEY not configured. Set in environment variables."
            )

        actions = {
            'render_video': self._render_video,
            'render_ad_set': self._render_ad_set,
            'generate_variations': self._generate_variations,
            'bulk_render': self._bulk_render,
            'create_text_video': self._create_text_video,
            'list_templates': self._list_templates,
            'check_status': self._check_status
        }

        if action not in actions:
            return AgentResult(
                success=False,
                data=None,
                message=f"Unknown action: {action}. Available: {list(actions.keys())}"
            )

        return actions[action](context)

    def _render_video(self, context: Dict[str, Any]) -> AgentResult:
        """Render a single video from template"""
        self.validate_context(context, ['template_id'])

        template_id = context['template_id']
        modifications = context.get('modifications', {})
        output_format = context.get('format', 'mp4')
        wait = context.get('wait', False)

        video_format = VideoFormat.MP4 if output_format == 'mp4' else VideoFormat.GIF

        try:
            if wait:
                # Render and wait for completion
                result = self.creatomate.render_and_wait(
                    template_id=template_id,
                    modifications=modifications,
                    output_format=video_format
                )

                video_ad = VideoAd(
                    name=context.get('name', f"Video - {template_id[:8]}"),
                    render_id=result.get('id', ''),
                    status=result.get('status', 'succeeded'),
                    format=output_format,
                    template_id=template_id,
                    url=result.get('url'),
                    modifications=modifications
                )

                return AgentResult(
                    success=True,
                    data={
                        'video': video_ad.__dict__,
                        'render_id': result.get('id'),
                        'url': result.get('url'),
                        'status': 'completed'
                    },
                    message=f"Video rendered successfully. URL: {result.get('url')}"
                )
            else:
                # Start render without waiting
                result = self.creatomate.render_from_template(
                    template_id=template_id,
                    modifications=modifications,
                    output_format=video_format
                )

                video_ad = VideoAd(
                    name=context.get('name', f"Video - {template_id[:8]}"),
                    render_id=result.render_id,
                    status=result.status,
                    format=output_format,
                    template_id=template_id,
                    modifications=modifications
                )

                return AgentResult(
                    success=True,
                    data={
                        'video': video_ad.__dict__,
                        'render_id': result.render_id,
                        'status': result.status
                    },
                    message=f"Video render started. Render ID: {result.render_id}"
                )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to render video: {str(e)}"
            )

    def _render_ad_set(self, context: Dict[str, Any]) -> AgentResult:
        """Render complete ad set with multiple format templates"""
        templates = context.get('templates', {})
        modifications = context.get('modifications', {})

        if not templates:
            return AgentResult(
                success=False,
                data=None,
                message="No templates provided. Provide dict of format:template_id"
            )

        renders = []
        errors = []

        for format_name, template_id in templates.items():
            try:
                result = self.creatomate.render_from_template(
                    template_id=template_id,
                    modifications=modifications
                )

                renders.append({
                    'format': format_name,
                    'render_id': result.render_id,
                    'status': result.status,
                    'template_id': template_id
                })

            except Exception as e:
                errors.append({
                    'format': format_name,
                    'error': str(e)
                })

        return AgentResult(
            success=len(renders) > 0,
            data={
                'renders': renders,
                'errors': errors,
                'total_rendered': len(renders)
            },
            message=f"Started {len(renders)} video renders across {len(templates)} formats"
        )

    def _generate_variations(self, context: Dict[str, Any]) -> AgentResult:
        """Generate multiple variations of the same ad"""
        self.validate_context(context, ['template_id', 'variations'])

        template_id = context['template_id']
        variations = context['variations']
        output_format = context.get('format', 'mp4')

        video_format = VideoFormat.MP4 if output_format == 'mp4' else VideoFormat.GIF

        results = []

        for i, modifications in enumerate(variations):
            try:
                result = self.creatomate.render_from_template(
                    template_id=template_id,
                    modifications=modifications,
                    output_format=video_format
                )

                results.append({
                    'variation': i + 1,
                    'render_id': result.render_id,
                    'status': result.status,
                    'modifications': modifications
                })

            except Exception as e:
                results.append({
                    'variation': i + 1,
                    'error': str(e)
                })

        return AgentResult(
            success=True,
            data={
                'variations': results,
                'total': len(results),
                'template_id': template_id
            },
            message=f"Generated {len(results)} video variations"
        )

    def _bulk_render(self, context: Dict[str, Any]) -> AgentResult:
        """Bulk render multiple videos with different data"""
        self.validate_context(context, ['template_id', 'data_list'])

        template_id = context['template_id']
        data_list = context['data_list']
        output_format = context.get('format', 'mp4')

        video_format = VideoFormat.MP4 if output_format == 'mp4' else VideoFormat.GIF

        try:
            results = self.creatomate.bulk_render(
                template_id=template_id,
                data_list=data_list,
                output_format=video_format
            )

            render_data = [
                {
                    'render_id': r.render_id,
                    'status': r.status,
                    'template_id': r.template_id
                }
                for r in results
            ]

            return AgentResult(
                success=True,
                data={
                    'renders': render_data,
                    'total': len(results),
                    'template_id': template_id
                },
                message=f"Started {len(results)} bulk video renders"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Bulk render failed: {str(e)}"
            )

    def _create_text_video(self, context: Dict[str, Any]) -> AgentResult:
        """Create a simple text-based video"""
        self.validate_context(context, ['text'])

        text = context['text']
        duration = context.get('duration', 5.0)
        format_name = context.get('format', 'feed')

        # Get format dimensions
        formats = self.config.settings.get('formats', {})
        fmt = formats.get(format_name, formats['feed'])

        try:
            result = self.creatomate.create_text_video(
                text=text,
                duration=duration,
                width=fmt['width'],
                height=fmt['height'],
                background_color=context.get('background_color', '#0A1628'),
                text_color=context.get('text_color', '#FFFFFF'),
                font_size=context.get('font_size', 80)
            )

            return AgentResult(
                success=True,
                data={
                    'render_id': result.render_id,
                    'status': result.status,
                    'text': text,
                    'format': format_name
                },
                message=f"Text video render started. Render ID: {result.render_id}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to create text video: {str(e)}"
            )

    def _list_templates(self, context: Dict[str, Any]) -> AgentResult:
        """List all available templates"""
        try:
            templates = self.creatomate.list_templates()

            return AgentResult(
                success=True,
                data={
                    'templates': templates,
                    'total': len(templates)
                },
                message=f"Found {len(templates)} templates"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to list templates: {str(e)}"
            )

    def _check_status(self, context: Dict[str, Any]) -> AgentResult:
        """Check status of a render"""
        self.validate_context(context, ['render_id'])

        render_id = context['render_id']

        try:
            result = self.creatomate.get_render_status(render_id)

            return AgentResult(
                success=True,
                data=result,
                message=f"Render status: {result.get('status')}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to get render status: {str(e)}"
            )

    def wait_and_download(
        self,
        render_id: str,
        save_dir: str = "./generated/videos"
    ) -> Optional[str]:
        """Wait for render and download the video"""
        if not self.creatomate:
            return None

        try:
            result = self.creatomate.wait_for_render(render_id)
            if result.get('status') == 'succeeded':
                url = result.get('url')
                if url:
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = f"{save_dir}/{render_id}.mp4"
                    return self.creatomate.download_video(url, save_path)
        except Exception as e:
            print(f"Download failed: {e}")

        return None
