"""
Design Agent
AI-powered ad creative generation using Leonardo.ai API

Generates professional ad images for Meta, Google, and display campaigns
with support for multiple formats, styles, and brand consistency.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

from ..base import BaseAgent, AgentConfig, AgentResult

try:
    from core.adapters.leonardo import (
        LeonardoAdapter,
        LeonardoModel,
        AspectRatio,
        GeneratedImage
    )
    LEONARDO_AVAILABLE = True
except ImportError:
    LEONARDO_AVAILABLE = False


@dataclass
class AdCreative:
    """Generated ad creative"""
    name: str
    prompt: str
    format: str
    aspect_ratio: tuple
    generation_id: str
    status: str
    image_url: Optional[str] = None
    model: str = "lightning"


class DesignAgent(BaseAgent):
    """
    AI Agent for generating ad creatives using Leonardo.ai API.

    Capabilities:
    - Generate ad images from product descriptions
    - Create multi-format ad sets (feed, story, display)
    - Apply brand-consistent styles
    - Generate variations for A/B testing
    - PhotoReal mode for ultra-realistic images

    Actions:
    - generate_ad: Generate a single ad image
    - generate_ad_set: Generate complete ad set (multiple formats)
    - generate_variations: Generate multiple variations of same concept

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
        self.leonardo: Optional[LeonardoAdapter] = None
        self._init_leonardo()

    def _init_leonardo(self):
        """Initialize Leonardo adapter if API key available"""
        if LEONARDO_AVAILABLE and os.getenv("LEONARDO_API_KEY"):
            try:
                self.leonardo = LeonardoAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize Leonardo: {e}")

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="DesignAgent",
            description="AI-powered ad creative generation with Leonardo.ai",
            version="2.0.0",
            model="leonardo-lightning-xl",
            temperature=0.7,
            settings={
                'supported_actions': [
                    'generate_ad',
                    'generate_ad_set',
                    'generate_variations'
                ],
                'default_model': 'lightning',
                'formats': {
                    'feed': 'SQUARE_HD',
                    'story': 'STORY_HD',
                    'display': 'WIDESCREEN_HD',
                    'portrait': 'PORTRAIT'
                },
                'styles': {
                    'modern': 'clean, minimalist, professional, high-contrast',
                    'luxury': 'elegant, premium, sophisticated, rich colors',
                    'energetic': 'vibrant, dynamic, bold colors, high energy',
                    'organic': 'natural, soft, warm tones, authentic',
                    'tech': 'futuristic, sleek, blue tones, digital',
                    'cinematic': 'cinematic lighting, dramatic, film quality'
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
                - style: Visual style (modern, luxury, energetic, organic, tech, cinematic)
                - format: Ad format (feed, story, display, portrait)
                - model: Leonardo model (lightning, photoreal, kino, diffusion)
                - photo_real: Use PhotoReal mode for realistic images
                - count: Number of variations (for generate_variations)

        Returns:
            AgentResult with generated creatives
        """
        action = context.get('action', 'generate_ad')

        if not LEONARDO_AVAILABLE:
            return AgentResult(
                success=False,
                data=None,
                message="Leonardo adapter not available. Install with: pip install requests"
            )

        if not self.leonardo:
            return AgentResult(
                success=False,
                data=None,
                message="LEONARDO_API_KEY not configured. Set in environment variables."
            )

        if action == 'generate_ad':
            return self._generate_ad(context)
        elif action == 'generate_ad_set':
            return self._generate_ad_set(context)
        elif action == 'generate_variations':
            return self._generate_variations(context)
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
        prompt_parts.append("8k resolution, professional lighting")

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
            'feed': AspectRatio.SQUARE_HD,
            'story': AspectRatio.STORY_HD,
            'display': AspectRatio.WIDESCREEN_HD,
            'portrait': AspectRatio.PORTRAIT,
            'square': AspectRatio.SQUARE
        }
        return mapping.get(format_name, AspectRatio.SQUARE_HD)

    def _get_model(self, model_name: str) -> LeonardoModel:
        """Map model name to LeonardoModel enum"""
        mapping = {
            'lightning': LeonardoModel.LEONARDO_LIGHTNING_XL,
            'photoreal': LeonardoModel.PHOTOREAL_V2,
            'kino': LeonardoModel.LEONARDO_KINO_XL,
            'diffusion': LeonardoModel.LEONARDO_DIFFUSION_XL,
            'vision': LeonardoModel.LEONARDO_VISION_XL,
            'anime': LeonardoModel.ANIME_PASTEL_DREAM,
            'dreamshaper': LeonardoModel.DREAMSHAPER_V7
        }
        return mapping.get(model_name, LeonardoModel.LEONARDO_LIGHTNING_XL)

    def _generate_ad(self, context: Dict[str, Any]) -> AgentResult:
        """Generate a single ad image"""
        self.validate_context(context, ['product'])

        prompt = self._build_prompt(context)
        format_name = context.get('format', 'feed')
        model_name = context.get('model', 'lightning')
        photo_real = context.get('photo_real', False)

        aspect_ratio = self._get_aspect_ratio(format_name)
        model = self._get_model(model_name)

        # Use PhotoReal model if requested
        if photo_real:
            model = LeonardoModel.PHOTOREAL_V2

        try:
            result = self.leonardo.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model,
                num_images=1,
                alchemy=True,
                photo_real=photo_real,
                negative_prompt="blurry, low quality, distorted, watermark, text, logo"
            )

            creative = AdCreative(
                name=f"{context['product'][:30]} - {format_name}",
                prompt=prompt,
                format=format_name,
                aspect_ratio=aspect_ratio.value,
                generation_id=result.generation_id,
                status=result.status,
                model=model_name
            )

            return AgentResult(
                success=True,
                data={
                    'creative': creative.__dict__,
                    'generation_id': result.generation_id,
                    'status': result.status,
                    'prompt_used': prompt
                },
                message=f"Ad creative generation started. Generation ID: {result.generation_id}"
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
        model_name = context.get('model', 'lightning')
        model = self._get_model(model_name)
        photo_real = context.get('photo_real', False)

        if photo_real:
            model = LeonardoModel.PHOTOREAL_V2

        creatives = []
        errors = []

        for format_name in formats:
            try:
                aspect_ratio = self._get_aspect_ratio(format_name)
                result = self.leonardo.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    model=model,
                    alchemy=True,
                    photo_real=photo_real,
                    negative_prompt="blurry, low quality, distorted, watermark, text, logo"
                )

                creatives.append({
                    'name': f"{context['product'][:30]} - {format_name}",
                    'format': format_name,
                    'generation_id': result.generation_id,
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
        model_name = context.get('model', 'lightning')
        photo_real = context.get('photo_real', False)

        aspect_ratio = self._get_aspect_ratio(format_name)
        model = self._get_model(model_name)

        if photo_real:
            model = LeonardoModel.PHOTOREAL_V2

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
                result = self.leonardo.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    model=model,
                    alchemy=True,
                    photo_real=photo_real,
                    negative_prompt="blurry, low quality, distorted, watermark, text, logo"
                )

                variations.append({
                    'variation': i + 1,
                    'modifier': modifier or 'base',
                    'generation_id': result.generation_id,
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

    def check_status(self, generation_id: str) -> Dict[str, Any]:
        """Check status of a generation"""
        if not self.leonardo:
            return {'error': 'Leonardo not initialized'}

        try:
            return self.leonardo.get_generation(generation_id)
        except Exception as e:
            return {'error': str(e)}

    def wait_and_download(self, generation_id: str, save_dir: str = "./generated") -> Optional[List[str]]:
        """Wait for completion and download all images"""
        if not self.leonardo:
            return None

        try:
            result = self.leonardo.wait_for_completion(generation_id)
            if result.get('status') == 'COMPLETE':
                images = result.get('generated_images', [])
                downloaded = []
                os.makedirs(save_dir, exist_ok=True)

                for i, img in enumerate(images):
                    url = img.get('url')
                    if url:
                        save_path = f"{save_dir}/{generation_id}_{i}.png"
                        self.leonardo.download_image(url, save_path)
                        downloaded.append(save_path)

                return downloaded
        except Exception as e:
            print(f"Download failed: {e}")

        return None

    def get_credits(self) -> Dict[str, Any]:
        """Get remaining API credits"""
        if not self.leonardo:
            return {'error': 'Leonardo not initialized'}

        try:
            user_info = self.leonardo.get_user_info()
            return {
                'api_credits': user_info.get('user_details', [{}])[0].get('apiConcurrencySlots', 0),
                'subscription_tokens': user_info.get('user_details', [{}])[0].get('subscriptionTokens', 0)
            }
        except Exception as e:
            return {'error': str(e)}
