"""
Creatomate API Adapter
Integration for automated video generation and editing
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class VideoFormat(Enum):
    """Output video formats"""
    MP4 = "mp4"
    GIF = "gif"
    PNG = "png"
    JPEG = "jpg"


class AspectRatio(Enum):
    """Common aspect ratios for video ads"""
    SQUARE = "1:1"           # Instagram Feed
    STORY = "9:16"           # Stories, Reels, TikTok
    WIDESCREEN = "16:9"      # YouTube, Display
    PORTRAIT = "4:5"         # Instagram Portrait
    LANDSCAPE = "3:2"        # Landscape


class Resolution(Enum):
    """Video resolutions"""
    SD = 480
    HD = 720
    FULL_HD = 1080
    QHD = 1440
    UHD_4K = 2160


@dataclass
class RenderResult:
    """Result of a video render"""
    render_id: str
    status: str
    url: Optional[str] = None
    template_id: str = ""
    format: str = "mp4"
    duration: float = 0.0


class CreatomateAdapter:
    """
    Creatomate API Adapter for automated video generation.

    Capabilities:
    - Render videos from templates
    - Dynamic text, image, and video insertion
    - Multiple output formats (MP4, GIF, PNG)
    - Bulk video generation
    - Template management

    Usage:
        adapter = CreatomateAdapter(api_key="your_key")
        result = adapter.render_from_template(
            template_id="your_template_id",
            modifications={
                "Title": "My Ad Title",
                "Video": "https://example.com/video.mp4"
            }
        )
    """

    BASE_URL = "https://api.creatomate.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CREATOMATE_API_KEY")
        if not self.api_key:
            raise ValueError("CREATOMATE_API_KEY is required")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def render_from_template(
        self,
        template_id: str,
        modifications: Dict[str, Any] = None,
        output_format: VideoFormat = VideoFormat.MP4,
        render_scale: float = 1.0,
        webhook_url: Optional[str] = None
    ) -> RenderResult:
        """
        Render a video from a template with dynamic data.

        Args:
            template_id: ID of the template from Creatomate dashboard
            modifications: Dict of element names and their values
            output_format: Output format (mp4, gif, png, jpg)
            render_scale: Scale factor (0.1 to 10.0, default 1.0)
            webhook_url: URL to call when render completes

        Returns:
            RenderResult with render_id and status
        """
        payload = {
            "template_id": template_id,
            "output_format": output_format.value,
            "render_scale": render_scale
        }

        if modifications:
            payload["modifications"] = modifications

        if webhook_url:
            payload["webhook_url"] = webhook_url

        response = requests.post(
            f"{self.BASE_URL}/renders",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()

        # API returns a list of renders
        if isinstance(data, list) and len(data) > 0:
            render_data = data[0]
        else:
            render_data = data

        return RenderResult(
            render_id=render_data.get("id", ""),
            status=render_data.get("status", "pending"),
            url=render_data.get("url"),
            template_id=template_id,
            format=output_format.value
        )

    def render_from_json(
        self,
        source: Dict[str, Any],
        output_format: VideoFormat = VideoFormat.MP4
    ) -> RenderResult:
        """
        Render a video from a JSON source definition.

        Args:
            source: JSON video definition
            output_format: Output format

        Returns:
            RenderResult with render_id and status
        """
        payload = {
            "source": source,
            "output_format": output_format.value
        }

        response = requests.post(
            f"{self.BASE_URL}/renders",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        render_data = data[0] if isinstance(data, list) else data

        return RenderResult(
            render_id=render_data.get("id", ""),
            status=render_data.get("status", "pending"),
            url=render_data.get("url"),
            format=output_format.value
        )

    def get_render_status(self, render_id: str) -> Dict[str, Any]:
        """
        Get the status of a render.

        Args:
            render_id: ID of the render

        Returns:
            Render status and details
        """
        response = requests.get(
            f"{self.BASE_URL}/renders/{render_id}",
            headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    def wait_for_render(
        self,
        render_id: str,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for a render to complete.

        Args:
            render_id: ID of the render
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final render data with URL
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self.get_render_status(render_id)
            status = result.get("status", "pending")

            if status == "succeeded":
                return result
            elif status == "failed":
                raise Exception(f"Render failed: {result.get('error_message', 'Unknown error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Render {render_id} did not complete within {max_wait} seconds")

    def render_and_wait(
        self,
        template_id: str,
        modifications: Dict[str, Any] = None,
        output_format: VideoFormat = VideoFormat.MP4
    ) -> Dict[str, Any]:
        """
        Render a video and wait for completion.

        Args:
            template_id: Template ID
            modifications: Dynamic data to insert
            output_format: Output format

        Returns:
            Complete render data with video URL
        """
        result = self.render_from_template(
            template_id=template_id,
            modifications=modifications,
            output_format=output_format
        )

        return self.wait_for_render(result.render_id)

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.

        Returns:
            List of template objects
        """
        response = requests.get(
            f"{self.BASE_URL}/templates",
            headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get details of a specific template.

        Args:
            template_id: Template ID

        Returns:
            Template details including elements
        """
        response = requests.get(
            f"{self.BASE_URL}/templates/{template_id}",
            headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    def bulk_render(
        self,
        template_id: str,
        data_list: List[Dict[str, Any]],
        output_format: VideoFormat = VideoFormat.MP4
    ) -> List[RenderResult]:
        """
        Render multiple videos from the same template with different data.

        Args:
            template_id: Template ID
            data_list: List of modification dicts
            output_format: Output format for all videos

        Returns:
            List of RenderResult objects
        """
        results = []

        for modifications in data_list:
            try:
                result = self.render_from_template(
                    template_id=template_id,
                    modifications=modifications,
                    output_format=output_format
                )
                results.append(result)
            except Exception as e:
                results.append(RenderResult(
                    render_id="",
                    status="failed",
                    template_id=template_id
                ))

        return results

    def create_text_video(
        self,
        text: str,
        duration: float = 5.0,
        width: int = 1080,
        height: int = 1080,
        background_color: str = "#0A1628",
        text_color: str = "#FFFFFF",
        font_size: int = 80
    ) -> RenderResult:
        """
        Create a simple text video programmatically.

        Args:
            text: Text to display
            duration: Video duration in seconds
            width: Video width
            height: Video height
            background_color: Background color hex
            text_color: Text color hex
            font_size: Font size in pixels

        Returns:
            RenderResult with render_id
        """
        source = {
            "output_format": "mp4",
            "width": width,
            "height": height,
            "duration": duration,
            "elements": [
                {
                    "type": "composition",
                    "track": 1,
                    "elements": [
                        {
                            "type": "shape",
                            "track": 1,
                            "fill_color": background_color,
                            "width": "100%",
                            "height": "100%"
                        },
                        {
                            "type": "text",
                            "track": 2,
                            "text": text,
                            "font_size": font_size,
                            "fill_color": text_color,
                            "x_alignment": "50%",
                            "y_alignment": "50%"
                        }
                    ]
                }
            ]
        }

        return self.render_from_json(source)

    def download_video(self, url: str, save_path: str) -> str:
        """
        Download rendered video to local file.

        Args:
            url: Video URL from render result
            save_path: Local path to save file

        Returns:
            Path to saved file
        """
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path
