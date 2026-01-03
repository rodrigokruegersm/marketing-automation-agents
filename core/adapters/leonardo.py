"""
Leonardo.ai API Adapter
Integration for AI image generation using Leonardo.ai API
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class LeonardoModel(Enum):
    """Available Leonardo.ai models"""
    LEONARDO_DIFFUSION_XL = "1e60896f-3c26-4296-8ecc-53e2afecc132"
    LEONARDO_LIGHTNING_XL = "b24e16ff-06e3-43eb-8d33-4416c2d75876"
    LEONARDO_KINO_XL = "aa77f04e-3eec-4034-9c07-d0f619684628"
    LEONARDO_VISION_XL = "5c232a9e-9061-4777-980a-ddc8e65647c6"
    PHOTOREAL_V2 = "b63f7119-31dc-4540-969b-2a9df997e173"
    ANIME_PASTEL_DREAM = "1aa0f478-51be-4efd-94e8-76bfc8f533af"
    DREAMSHAPER_V7 = "ac614f96-1082-45bf-be9d-757f2d31c174"


class AspectRatio(Enum):
    """Common aspect ratios for ads"""
    SQUARE = (512, 512)           # Instagram Feed
    SQUARE_HD = (1024, 1024)      # High quality square
    STORY = (576, 1024)           # Instagram/Facebook Stories
    STORY_HD = (768, 1344)        # HD Stories
    WIDESCREEN = (1024, 576)      # YouTube, Display Ads
    WIDESCREEN_HD = (1344, 768)   # HD Widescreen
    PORTRAIT = (768, 1024)        # Portrait format


@dataclass
class GeneratedImage:
    """Represents a generated image"""
    generation_id: str
    status: str
    images: List[Dict] = None
    prompt: str = ""
    model_id: str = ""

    def __post_init__(self):
        if self.images is None:
            self.images = []


class LeonardoAdapter:
    """
    Leonardo.ai API Adapter for AI image generation.

    Capabilities:
    - Text-to-image generation
    - Multiple aspect ratios for different ad formats
    - Multiple AI models (PhotoReal, Lightning, Kino, etc.)
    - High quality outputs for advertising

    Usage:
        adapter = LeonardoAdapter(api_key="your_key")
        result = adapter.generate_image(
            prompt="Professional business woman using laptop",
            aspect_ratio=AspectRatio.SQUARE,
            model=LeonardoModel.PHOTOREAL_V2
        )
    """

    BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LEONARDO_API_KEY")
        if not self.api_key:
            raise ValueError("LEONARDO_API_KEY is required")

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        model: LeonardoModel = LeonardoModel.LEONARDO_LIGHTNING_XL,
        num_images: int = 1,
        negative_prompt: str = "",
        guidance_scale: float = 7.0,
        public: bool = False,
        alchemy: bool = True,
        photo_real: bool = False,
        preset_style: str = None
    ) -> GeneratedImage:
        """
        Generate an image from text prompt.

        Args:
            prompt: Text description of the image
            aspect_ratio: Image aspect ratio (dimensions)
            model: Leonardo model to use
            num_images: Number of images to generate (1-4)
            negative_prompt: What to avoid in the image
            guidance_scale: How closely to follow prompt (1-20)
            public: Whether image is public on Leonardo
            alchemy: Use Alchemy for better quality
            photo_real: Use PhotoReal mode
            preset_style: Style preset (CINEMATIC, CREATIVE, etc.)

        Returns:
            GeneratedImage with generation_id and status
        """
        width, height = aspect_ratio.value

        payload = {
            "prompt": prompt,
            "modelId": model.value,
            "width": width,
            "height": height,
            "num_images": min(num_images, 4),
            "guidance_scale": guidance_scale,
            "public": public,
            "alchemy": alchemy,
        }

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if photo_real:
            payload["photoReal"] = True
            payload["photoRealVersion"] = "v2"

        if preset_style:
            payload["presetStyle"] = preset_style

        response = requests.post(
            f"{self.BASE_URL}/generations",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        generation_data = data.get("sdGenerationJob", {})

        return GeneratedImage(
            generation_id=generation_data.get("generationId", ""),
            status="PENDING",
            prompt=prompt,
            model_id=model.value
        )

    def get_generation(self, generation_id: str) -> Dict[str, Any]:
        """
        Get the status and results of a generation.

        Args:
            generation_id: The generation ID from generate_image

        Returns:
            Generation data with status and images
        """
        response = requests.get(
            f"{self.BASE_URL}/generations/{generation_id}",
            headers=self.headers
        )
        response.raise_for_status()

        return response.json().get("generations_by_pk", {})

    def wait_for_completion(
        self,
        generation_id: str,
        max_wait: int = 120,
        poll_interval: int = 3
    ) -> Dict[str, Any]:
        """
        Wait for a generation to complete.

        Args:
            generation_id: The generation ID to monitor
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final generation data with images
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self.get_generation(generation_id)
            status = result.get("status", "PENDING")

            if status == "COMPLETE":
                return result
            elif status == "FAILED":
                raise Exception(f"Generation failed: {result.get('error', 'Unknown error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Generation {generation_id} did not complete within {max_wait} seconds")

    def generate_and_wait(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        model: LeonardoModel = LeonardoModel.LEONARDO_LIGHTNING_XL,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image and wait for completion.

        Args:
            prompt: Text description
            aspect_ratio: Image dimensions
            model: Model to use
            **kwargs: Additional parameters for generate_image

        Returns:
            Complete generation data with image URLs
        """
        result = self.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            model=model,
            **kwargs
        )

        return self.wait_for_completion(result.generation_id)

    def generate_ad_set(
        self,
        prompt: str,
        formats: List[str] = None,
        model: LeonardoModel = LeonardoModel.LEONARDO_LIGHTNING_XL
    ) -> List[GeneratedImage]:
        """
        Generate a complete set of ad images in multiple formats.

        Args:
            prompt: Base prompt for all images
            formats: List of format types ('feed', 'story', 'display')
            model: Model to use

        Returns:
            List of GeneratedImage for each format
        """
        if formats is None:
            formats = ['feed', 'story', 'display']

        format_mapping = {
            'feed': AspectRatio.SQUARE_HD,
            'story': AspectRatio.STORY_HD,
            'display': AspectRatio.WIDESCREEN_HD,
            'portrait': AspectRatio.PORTRAIT
        }

        results = []

        for fmt in formats:
            aspect_ratio = format_mapping.get(fmt, AspectRatio.SQUARE)
            result = self.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model
            )
            results.append(result)

        return results

    def get_user_info(self) -> Dict[str, Any]:
        """Get user account information including credits"""
        response = requests.get(
            f"{self.BASE_URL}/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_models(self) -> List[Dict[str, Any]]:
        """List available platform models"""
        response = requests.get(
            f"{self.BASE_URL}/platformModels",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("custom_models", [])

    def download_image(self, url: str, save_path: str) -> str:
        """Download generated image to local file"""
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path
