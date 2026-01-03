"""
Design Agent
AI-powered ad creative generation using Freepik API

Generates professional ad images for Meta, Google, and display campaigns
with support for multiple formats, styles, and brand consistency.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

from ..base import BaseAgent, AgentConfig, AgentResult

try:
    from core.adapters.freepik import (
        FreepikAdapter,
        FreepikModel,
        FreepikEngine,
        AspectRatio,
        GeneratedImage
    )
    FREEPIK_AVAILABLE = True
except ImportError:
    FREEPIK_AVAILABLE = False


@dataclass
class AdCreative:
    """Generated ad creative"""
    name: str
    prompt: str
    format: str
    aspect_ratio: str
    task_id: str
    status: str
    image_url: Optional[str] = None
    model: str = "realism"


class DesignAgent(BaseAgent):
    """
    AI Agent for generating ad creatives using Freepik API.

    Capabilities:
    - Generate ad images from product descriptions
    - Create multi-format ad sets (feed, story, display)
    - Apply brand-consistent styles
    - Generate variations for A/B testing
    - Use reference images for style transfer

    Actions:
    - generate_ad: Generate a single ad image
    - generate_ad_set: Generate complete ad set (multiple formats)
    - generate_variations: Generate multiple variations of same concept
    - style_transfer: Apply style from reference image

    Usage:
        agent = DesignAgent()
        result = agent.run({
            'action': 'generate_ad',
            'product': 'Premium fitness coaching app',
            'audience': 'Men 25-40 interested in muscle building',
            'style': 'modern, high-energy, professional',
            'format': 'feed'
        })
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.freepik: Optional[FreepikAdapter] = None
        self._init_freepik()

    def _init_freepik(self):
        """Initialize Freepik adapter if API key available"""
        if FREEPIK_AVAILABLE and os.getenv("FREEPIK_API_KEY"):
            try:
                self.freepik = FreepikAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize Freepik: {e}")

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="DesignAgent",
            description="AI-powered ad creative generation with Freepik",
            version="1.0.0",
            model="freepik-mystic",
            temperature=0.7,
            settings={
                'supported_actions': [
                    'generate_ad',
                    'generate_ad_set',
                    'generate_variations',
                    'style_transfer'
                ],
                'default_model': 'realism',
                'formats': {
                    'feed': 'square_1_1',
                    'story': 'social_story_9_16',
                    'display': 'widescreen_16_9',
                    'portrait': 'portrait_4_5'
                },
                'styles': {
                    'modern': 'clean, minimalist, professional, high-contrast',
                    'luxury': 'elegant, premium, sophisticated, rich colors',
                    'energetic': 'vibrant, dynamic, bold colors, high energy',
                    'organic': 'natural, soft, warm tones, authentic',
                    'tech': 'futuristic, sleek, blue tones, digital'
                }
            }
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute design agent action.

        Args:
            context: Dictionary with:
                - action: Action to perform
                - product: Product/service description
                - audience: Target audience
                - style: Visual style (modern, luxury, energetic, organic, tech)
                - format: Ad format (feed, story, display, portrait)
                - model: Freepik model (realism, fluid, zen, super_real)
                - reference_image: Path to style reference image (optional)
                - count: Number of variations (for generate_variations)

        Returns:
            AgentResult with generated creatives
        """
        action = context.get('action', 'generate_ad')

        if not FREEPIK_AVAILABLE:
            return AgentResult(
                success=False,
                data=None,
                message="Freepik adapter not available. Install with: pip install requests"
            )

        if not self.freepik:
            return AgentResult(
                success=False,
                data=None,
                message="FREEPIK_API_KEY not configured. Set in environment variables."
            )

        if action == 'generate_ad':
            return self._generate_ad(context)
        elif action == 'generate_ad_set':
            return self._generate_ad_set(context)
        elif action == 'generate_variations':
            return self._generate_variations(context)
        elif action == 'style_transfer':
            return self._style_transfer(context)
        else:
            return AgentResult(
                success=False,
                data=None,
                message=f"Unknown action: {action}"
            )

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build optimized prompt for ad creative generation"""
        product = context.get('product', '')
        audience = context.get('audience', '')
        style_key = context.get('style', 'modern')
        custom_prompt = context.get('prompt', '')

        # Get style description
        styles = self.config.settings.get('styles', {})
        style_desc = styles.get(style_key, style_key)

        # Build comprehensive prompt
        prompt_parts = []

        if custom_prompt:
            prompt_parts.append(custom_prompt)
        else:
            prompt_parts.append(f"Professional advertisement for {product}")

        prompt_parts.append(f"Style: {style_desc}")
        prompt_parts.append("High quality, commercial photography")
        prompt_parts.append("Perfect for digital advertising")

        if audience:
            # Infer visual elements from audience
            if 'men' in audience.lower():
                prompt_parts.append("masculine aesthetic")
            elif 'women' in audience.lower():
                prompt_parts.append("feminine aesthetic")

        return ", ".join(prompt_parts)

    def _get_aspect_ratio(self, format_name: str) -> AspectRatio:
        """Map format name to AspectRatio enum"""
        mapping = {
            'feed': AspectRatio.SQUARE,
            'story': AspectRatio.STORY,
            'display': AspectRatio.WIDESCREEN,
            'portrait': AspectRatio.PORTRAIT,
            'landscape': AspectRatio.LANDSCAPE
        }
        return mapping.get(format_name, AspectRatio.SQUARE)

    def _get_model(self, model_name: str) -> FreepikModel:
        """Map model name to FreepikModel enum"""
        mapping = {
            'realism': FreepikModel.REALISM,
            'fluid': FreepikModel.FLUID,
            'zen': FreepikModel.ZEN,
            'flexible': FreepikModel.FLEXIBLE,
            'super_real': FreepikModel.SUPER_REAL,
            'editorial': FreepikModel.EDITORIAL
        }
        return mapping.get(model_name, FreepikModel.REALISM)

    def _generate_ad(self, context: Dict[str, Any]) -> AgentResult:
        """Generate a single ad image"""
        self.validate_context(context, ['product'])

        prompt = self._build_prompt(context)
        format_name = context.get('format', 'feed')
        model_name = context.get('model', 'realism')

        aspect_ratio = self._get_aspect_ratio(format_name)
        model = self._get_model(model_name)

        try:
            result = self.freepik.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model,
                resolution="2k",
                hdr=60,
                creative_detailing=40
            )

            creative = AdCreative(
                name=f"{context['product'][:30]} - {format_name}",
                prompt=prompt,
                format=format_name,
                aspect_ratio=aspect_ratio.value,
                task_id=result.task_id,
                status=result.status,
                model=model_name
            )

            return AgentResult(
                success=True,
                data={
                    'creative': creative.__dict__,
                    'task_id': result.task_id,
                    'status': result.status,
                    'prompt_used': prompt
                },
                message=f"Ad creative generation started. Task ID: {result.task_id}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to generate ad: {str(e)}"
            )

    def _generate_ad_set(self, context: Dict[str, Any]) -> AgentResult:
        """Generate complete ad set in multiple formats"""
        self.validate_context(context, ['product'])

        formats = context.get('formats', ['feed', 'story', 'display'])
        prompt = self._build_prompt(context)
        model_name = context.get('model', 'realism')
        model = self._get_model(model_name)

        creatives = []
        errors = []

        for format_name in formats:
            try:
                aspect_ratio = self._get_aspect_ratio(format_name)
                result = self.freepik.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    model=model,
                    resolution="2k"
                )

                creatives.append({
                    'name': f"{context['product'][:30]} - {format_name}",
                    'format': format_name,
                    'task_id': result.task_id,
                    'status': result.status,
                    'aspect_ratio': aspect_ratio.value
                })

            except Exception as e:
                errors.append({
                    'format': format_name,
                    'error': str(e)
                })

        return AgentResult(
            success=len(creatives) > 0,
            data={
                'creatives': creatives,
                'errors': errors,
                'prompt_used': prompt,
                'total_generated': len(creatives)
            },
            message=f"Generated {len(creatives)} ad creatives across {len(formats)} formats"
        )

    def _generate_variations(self, context: Dict[str, Any]) -> AgentResult:
        """Generate multiple variations of the same concept"""
        self.validate_context(context, ['product'])

        count = min(context.get('count', 3), 10)  # Max 10 variations
        format_name = context.get('format', 'feed')
        model_name = context.get('model', 'realism')

        aspect_ratio = self._get_aspect_ratio(format_name)
        model = self._get_model(model_name)

        variations = []
        base_prompt = self._build_prompt(context)

        # Generate variations with slight prompt modifications
        variation_modifiers = [
            "",
            "close-up shot",
            "wide angle",
            "dramatic lighting",
            "soft natural light",
            "bold colors",
            "subtle tones",
            "action shot",
            "lifestyle setting",
            "studio background"
        ]

        for i in range(count):
            modifier = variation_modifiers[i % len(variation_modifiers)]
            prompt = f"{base_prompt}, {modifier}" if modifier else base_prompt

            try:
                result = self.freepik.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    model=model,
                    resolution="2k"
                )

                variations.append({
                    'variation': i + 1,
                    'modifier': modifier or 'base',
                    'task_id': result.task_id,
                    'status': result.status,
                    'prompt': prompt
                })

            except Exception as e:
                variations.append({
                    'variation': i + 1,
                    'error': str(e)
                })

        return AgentResult(
            success=True,
            data={
                'variations': variations,
                'format': format_name,
                'total': len(variations)
            },
            message=f"Generated {len(variations)} variations"
        )

    def _style_transfer(self, context: Dict[str, Any]) -> AgentResult:
        """Apply style from reference image"""
        self.validate_context(context, ['product', 'reference_image'])

        reference_path = context['reference_image']
        format_name = context.get('format', 'feed')
        model_name = context.get('model', 'realism')

        try:
            # Convert reference image to base64
            style_reference = self.freepik.image_to_base64(reference_path)

            prompt = self._build_prompt(context)
            aspect_ratio = self._get_aspect_ratio(format_name)
            model = self._get_model(model_name)

            result = self.freepik.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model,
                style_reference=style_reference,
                resolution="2k"
            )

            return AgentResult(
                success=True,
                data={
                    'task_id': result.task_id,
                    'status': result.status,
                    'prompt_used': prompt,
                    'reference_used': reference_path
                },
                message=f"Style transfer started. Task ID: {result.task_id}"
            )

        except FileNotFoundError:
            return AgentResult(
                success=False,
                data=None,
                message=f"Reference image not found: {reference_path}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Style transfer failed: {str(e)}"
            )

    def check_status(self, task_id: str) -> Dict[str, Any]:
        """Check status of a generation task"""
        if not self.freepik:
            return {'error': 'Freepik not initialized'}

        try:
            return self.freepik.get_task_status(task_id)
        except Exception as e:
            return {'error': str(e)}

    def download_result(self, task_id: str, save_dir: str = "./generated") -> Optional[str]:
        """Download completed generation to local file"""
        if not self.freepik:
            return None

        try:
            status = self.freepik.wait_for_completion(task_id)
            if status.get('status') == 'COMPLETED':
                images = status.get('generated', [])
                if images:
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = f"{save_dir}/{task_id}.png"
                    return self.freepik.download_image(images[0], save_path)
        except Exception as e:
            print(f"Download failed: {e}")

        return None
