"""
CopyForge Agent
Generates high-converting ad copy, headlines, and marketing text
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..base import BaseAgent, AgentConfig, AgentResult


@dataclass
class CopyRequest:
    """Request for copy generation"""
    type: str  # headline, primary_text, description, hook, cta
    product: str
    audience: str
    tone: str = "professional"
    platform: str = "meta"
    variations: int = 3
    max_length: Optional[int] = None
    context: Optional[str] = None


@dataclass
class GeneratedCopy:
    """Generated copy output"""
    type: str
    text: str
    confidence: float
    reasoning: str
    platform_optimized: bool = True


class CopyForgeAgent(BaseAgent):
    """
    AI Agent for generating marketing copy.

    Capabilities:
    - Generate ad headlines (multiple variations)
    - Create primary text for Meta ads
    - Write compelling hooks for video ads
    - Generate CTAs optimized for conversions
    - A/B test copy variations

    Usage:
        agent = CopyForgeAgent()
        result = agent.run({
            'type': 'headline',
            'product': 'Online course about marketing',
            'audience': 'Entrepreneurs aged 25-45',
            'tone': 'urgent',
            'variations': 5
        })
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="CopyForge",
            description="AI-powered copywriting agent for ads and marketing",
            version="1.0.0",
            model="claude-3-opus",
            temperature=0.8,  # Higher for creativity
            settings={
                'default_variations': 3,
                'supported_platforms': ['meta', 'google', 'tiktok', 'linkedin'],
                'supported_types': ['headline', 'primary_text', 'description', 'hook', 'cta', 'script']
            }
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Generate marketing copy based on context.

        Args:
            context: Dictionary with:
                - type: Type of copy (headline, primary_text, etc.)
                - product: Product/service description
                - audience: Target audience description
                - tone: Desired tone (professional, urgent, casual, etc.)
                - platform: Target platform (meta, google, tiktok)
                - variations: Number of variations to generate
                - max_length: Maximum character length
                - context: Additional context

        Returns:
            AgentResult with generated copy variations
        """
        # Validate required fields
        self.validate_context(context, ['type', 'product', 'audience'])

        copy_type = context.get('type', 'headline')
        product = context['product']
        audience = context['audience']
        tone = context.get('tone', 'professional')
        platform = context.get('platform', 'meta')
        variations = context.get('variations', 3)

        # TODO: Integrate with LLM (Claude/GPT) for actual generation
        # For now, return placeholder structure

        generated = []

        for i in range(variations):
            generated.append(GeneratedCopy(
                type=copy_type,
                text=f"[Generated {copy_type} #{i+1} for {product}]",
                confidence=0.85,
                reasoning=f"Optimized for {audience} with {tone} tone on {platform}",
                platform_optimized=True
            ))

        return AgentResult(
            success=True,
            data={
                'copies': [
                    {
                        'type': g.type,
                        'text': g.text,
                        'confidence': g.confidence,
                        'reasoning': g.reasoning
                    } for g in generated
                ],
                'request': {
                    'type': copy_type,
                    'product': product,
                    'audience': audience,
                    'tone': tone,
                    'platform': platform
                }
            },
            message=f"Generated {len(generated)} {copy_type} variations"
        )

    def generate_headlines(self, product: str, audience: str, count: int = 5) -> List[str]:
        """Generate headline variations"""
        result = self.run({
            'type': 'headline',
            'product': product,
            'audience': audience,
            'variations': count
        })

        if result.success:
            return [c['text'] for c in result.data['copies']]
        return []

    def generate_hooks(self, product: str, audience: str, count: int = 3) -> List[str]:
        """Generate video hook variations (first 3 seconds)"""
        result = self.run({
            'type': 'hook',
            'product': product,
            'audience': audience,
            'variations': count,
            'max_length': 50
        })

        if result.success:
            return [c['text'] for c in result.data['copies']]
        return []

    def generate_ad_set(self, product: str, audience: str, platform: str = 'meta') -> Dict:
        """Generate complete ad copy set (headline, primary, description, CTA)"""
        types = ['headline', 'primary_text', 'description', 'cta']
        ad_set = {}

        for copy_type in types:
            result = self.run({
                'type': copy_type,
                'product': product,
                'audience': audience,
                'platform': platform,
                'variations': 3
            })

            if result.success:
                ad_set[copy_type] = result.data['copies']

        return ad_set
