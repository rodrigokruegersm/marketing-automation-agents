"""
Freepik API Adapter
Integration for AI image generation using Freepik's Mystic API
"""

import os
import time
import base64
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class FreepikModel(Enum):
    """Available Freepik AI models"""
    REALISM = "realism"
    FLUID = "fluid"
    ZEN = "zen"
    FLEXIBLE = "flexible"
    SUPER_REAL = "super_real"
    EDITORIAL = "editorial_portraits"


class FreepikEngine(Enum):
    """Available rendering engines"""
    AUTOMATIC = "automatic"
    ILLUSIO = "magnific_illusio"  # Smoother, landscapes, nature
    SHARPY = "magnific_sharpy"   # Realistic photographs, detailed
    SPARKLE = "magnific_sparkle" # Balance between Illusio and Sharpy


class AspectRatio(Enum):
    """Common aspect ratios for ads"""
    SQUARE = "square_1_1"           # Instagram Feed, Facebook
    STORY = "social_story_9_16"     # Instagram/Facebook Stories
    WIDESCREEN = "widescreen_16_9"  # YouTube, Display Ads
    PORTRAIT = "portrait_4_5"       # Instagram Portrait
    LANDSCAPE = "landscape_3_2"     # Standard Landscape


@dataclass
class GeneratedImage:
    """Represents a generated image"""
    task_id: str
    status: str
    url: Optional[str] = None
    prompt: str = ""
    model: str = ""
    aspect_ratio: str = ""
    created_at: str = ""


class FreepikAdapter:
    """
    Freepik API Adapter for AI image generation.

    Capabilities:
    - Text-to-image generation
    - Multiple aspect ratios for different ad formats
    - Style and structure references
    - Multiple AI models (realism, fluid, etc.)

    Usage:
        adapter = FreepikAdapter(api_key="your_key")
        result = adapter.generate_image(
            prompt="Professional business woman using laptop",
            aspect_ratio=AspectRatio.SQUARE,
            model=FreepikModel.REALISM
        )
    """

    BASE_URL = "https://api.freepik.com/v1/ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY")
        if not self.api_key:
            raise ValueError("FREEPIK_API_KEY is required")

        self.headers = {
            "Content-Type": "application/json",
            "x-freepik-api-key": self.api_key
        }

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        model: FreepikModel = FreepikModel.REALISM,
        engine: FreepikEngine = FreepikEngine.AUTOMATIC,
        resolution: str = "2k",
        style_reference: Optional[str] = None,
        structure_reference: Optional[str] = None,
        hdr: int = 50,
        creative_detailing: int = 33,
        webhook_url: Optional[str] = None
    ) -> GeneratedImage:
        """
        Generate an image from text prompt.

        Args:
            prompt: Text description of the image
            aspect_ratio: Image aspect ratio
            model: AI model to use
            engine: Rendering engine
            resolution: Output resolution (1k, 2k, 4k)
            style_reference: Base64 image for style transfer
            structure_reference: Base64 image for structure/layout
            hdr: Detail level (0-100)
            creative_detailing: Creative enhancement (0-100)
            webhook_url: Callback URL for async notifications

        Returns:
            GeneratedImage with task_id and status
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio.value,
            "model": model.value,
            "engine": engine.value,
            "resolution": resolution,
            "hdr": hdr,
            "creative_detailing": creative_detailing,
            "filter_nsfw": True
        }

        if webhook_url:
            payload["webhook_url"] = webhook_url

        if style_reference:
            payload["style_reference"] = style_reference
            payload["adherence"] = 50

        if structure_reference:
            payload["structure_reference"] = structure_reference
            payload["structure_strength"] = 50

        response = requests.post(
            f"{self.BASE_URL}/mystic",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json().get("data", {})

        return GeneratedImage(
            task_id=data.get("task_id", ""),
            status=data.get("status", "UNKNOWN"),
            prompt=prompt,
            model=model.value,
            aspect_ratio=aspect_ratio.value
        )

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a generation task.

        Args:
            task_id: The task ID from generate_image

        Returns:
            Task status and generated image URLs if complete
        """
        response = requests.get(
            f"{self.BASE_URL}/mystic/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()

        return response.json().get("data", {})

    def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 120,
        poll_interval: int = 3
    ) -> Dict[str, Any]:
        """
        Wait for a task to complete.

        Args:
            task_id: The task ID to monitor
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final task data with generated image URLs
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = self.get_task_status(task_id)

            if status.get("status") == "COMPLETED":
                return status
            elif status.get("status") == "FAILED":
                raise Exception(f"Task failed: {status.get('error', 'Unknown error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {max_wait} seconds")

    def generate_and_wait(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        model: FreepikModel = FreepikModel.REALISM,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image and wait for completion.

        Args:
            prompt: Text description
            aspect_ratio: Image aspect ratio
            model: AI model to use
            **kwargs: Additional parameters for generate_image

        Returns:
            Complete task data with image URLs
        """
        result = self.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            model=model,
            **kwargs
        )

        return self.wait_for_completion(result.task_id)

    def generate_ad_set(
        self,
        prompt: str,
        formats: List[str] = None,
        model: FreepikModel = FreepikModel.REALISM
    ) -> List[GeneratedImage]:
        """
        Generate a complete set of ad images in multiple formats.

        Args:
            prompt: Base prompt for all images
            formats: List of format types ('feed', 'story', 'display')
            model: AI model to use

        Returns:
            List of GeneratedImage for each format
        """
        if formats is None:
            formats = ['feed', 'story', 'display']

        format_mapping = {
            'feed': AspectRatio.SQUARE,
            'story': AspectRatio.STORY,
            'display': AspectRatio.WIDESCREEN,
            'portrait': AspectRatio.PORTRAIT,
            'landscape': AspectRatio.LANDSCAPE
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

    def image_to_base64(self, image_path: str) -> str:
        """Convert an image file to base64 string"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def download_image(self, url: str, save_path: str) -> str:
        """Download generated image to local file"""
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path
