"""
HeyGen API Adapter
Integration for AI avatar videos and lip sync
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class VideoAspectRatio(Enum):
    """Video aspect ratios"""
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"


class VideoQuality(Enum):
    """Video quality options"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AvatarType(Enum):
    """Avatar types"""
    TALKING_PHOTO = "talking_photo"
    AVATAR = "avatar"
    STUDIO_AVATAR = "studio_avatar"


@dataclass
class Avatar:
    """HeyGen avatar"""
    avatar_id: str
    name: str
    avatar_type: str
    preview_url: Optional[str] = None
    gender: Optional[str] = None


@dataclass
class VideoResult:
    """Result of video generation"""
    video_id: str
    status: str
    video_url: Optional[str] = None
    duration: float = 0.0
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None


class HeyGenAdapter:
    """
    HeyGen API Adapter for AI avatar videos and lip sync.

    Capabilities:
    - List available avatars (custom and stock)
    - Create videos with talking avatars
    - Lip sync with custom audio
    - Upload custom talking photos
    - Multiple aspect ratios and qualities

    Usage:
        adapter = HeyGenAdapter(api_key="your_key")

        # List avatars
        avatars = adapter.list_avatars()

        # Create video from text
        result = adapter.create_video_from_text(
            avatar_id="your_avatar_id",
            text="Olá! Este é um vídeo gerado por IA.",
            voice_id="pt-BR-voice"
        )

        # Wait for completion
        video = adapter.wait_for_video(result.video_id)
        print(f"Video URL: {video.video_url}")
    """

    BASE_URL = "https://api.heygen.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY is required")

        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def list_avatars(self) -> List[Avatar]:
        """
        List all available avatars.

        Returns:
            List of Avatar objects
        """
        response = requests.get(
            f"{self.BASE_URL}/v2/avatars",
            headers=self.headers
        )
        response.raise_for_status()

        data = response.json()
        avatars = []

        for a in data.get("data", {}).get("avatars", []):
            avatars.append(Avatar(
                avatar_id=a.get("avatar_id", ""),
                name=a.get("avatar_name", ""),
                avatar_type=a.get("type", "avatar"),
                preview_url=a.get("preview_image_url"),
                gender=a.get("gender")
            ))

        return avatars

    def list_talking_photos(self) -> List[Avatar]:
        """
        List all talking photo avatars (custom uploaded).

        Returns:
            List of Avatar objects (talking photos only)
        """
        response = requests.get(
            f"{self.BASE_URL}/v2/talking_photo",
            headers=self.headers
        )
        response.raise_for_status()

        data = response.json()
        avatars = []

        for a in data.get("data", {}).get("talking_photos", []):
            avatars.append(Avatar(
                avatar_id=a.get("talking_photo_id", ""),
                name=a.get("talking_photo_name", ""),
                avatar_type="talking_photo",
                preview_url=a.get("preview_image_url")
            ))

        return avatars

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        List all available voices.

        Returns:
            List of voice dicts
        """
        response = requests.get(
            f"{self.BASE_URL}/v2/voices",
            headers=self.headers
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("voices", [])

    def create_video_from_text(
        self,
        avatar_id: str,
        text: str,
        voice_id: str,
        aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE,
        quality: VideoQuality = VideoQuality.HIGH,
        avatar_type: AvatarType = AvatarType.AVATAR,
        test_mode: bool = False
    ) -> VideoResult:
        """
        Create a video with avatar speaking the given text.

        Args:
            avatar_id: ID of the avatar to use
            text: Text for the avatar to speak
            voice_id: ID of the voice to use
            aspect_ratio: Video aspect ratio
            quality: Video quality
            avatar_type: Type of avatar
            test_mode: If True, create a watermarked test video (free)

        Returns:
            VideoResult with video_id and status
        """
        url = f"{self.BASE_URL}/v2/video/generate"

        # Build video input based on avatar type
        if avatar_type == AvatarType.TALKING_PHOTO:
            avatar_input = {
                "type": "talking_photo",
                "talking_photo_id": avatar_id,
                "voice_id": voice_id,
                "input_text": text
            }
        else:
            avatar_input = {
                "type": "avatar",
                "avatar_id": avatar_id,
                "voice_id": voice_id,
                "input_text": text
            }

        payload = {
            "video_inputs": [avatar_input],
            "dimension": {
                "width": 1920 if aspect_ratio == VideoAspectRatio.LANDSCAPE else (1080 if aspect_ratio == VideoAspectRatio.PORTRAIT else 1080),
                "height": 1080 if aspect_ratio == VideoAspectRatio.LANDSCAPE else (1920 if aspect_ratio == VideoAspectRatio.PORTRAIT else 1080)
            },
            "test": test_mode
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        video_data = data.get("data", {})

        return VideoResult(
            video_id=video_data.get("video_id", ""),
            status="pending"
        )

    def create_video_from_audio(
        self,
        avatar_id: str,
        audio_url: str,
        aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE,
        avatar_type: AvatarType = AvatarType.AVATAR,
        test_mode: bool = False
    ) -> VideoResult:
        """
        Create a video with avatar lip synced to provided audio.

        Args:
            avatar_id: ID of the avatar to use
            audio_url: URL to the audio file
            aspect_ratio: Video aspect ratio
            avatar_type: Type of avatar
            test_mode: If True, create a watermarked test video

        Returns:
            VideoResult with video_id and status
        """
        url = f"{self.BASE_URL}/v2/video/generate"

        if avatar_type == AvatarType.TALKING_PHOTO:
            avatar_input = {
                "type": "talking_photo",
                "talking_photo_id": avatar_id,
                "voice_type": "audio",
                "input_audio": audio_url
            }
        else:
            avatar_input = {
                "type": "avatar",
                "avatar_id": avatar_id,
                "voice_type": "audio",
                "input_audio": audio_url
            }

        payload = {
            "video_inputs": [avatar_input],
            "dimension": {
                "width": 1920 if aspect_ratio == VideoAspectRatio.LANDSCAPE else (1080 if aspect_ratio == VideoAspectRatio.PORTRAIT else 1080),
                "height": 1080 if aspect_ratio == VideoAspectRatio.LANDSCAPE else (1920 if aspect_ratio == VideoAspectRatio.PORTRAIT else 1080)
            },
            "test": test_mode
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        video_data = data.get("data", {})

        return VideoResult(
            video_id=video_data.get("video_id", ""),
            status="pending"
        )

    def get_video_status(self, video_id: str) -> VideoResult:
        """
        Get the status of a video generation.

        Args:
            video_id: ID of the video

        Returns:
            VideoResult with current status
        """
        response = requests.get(
            f"{self.BASE_URL}/v1/video_status.get",
            headers=self.headers,
            params={"video_id": video_id}
        )
        response.raise_for_status()

        data = response.json()
        video_data = data.get("data", {})

        return VideoResult(
            video_id=video_id,
            status=video_data.get("status", "unknown"),
            video_url=video_data.get("video_url"),
            duration=video_data.get("duration", 0.0),
            thumbnail_url=video_data.get("thumbnail_url"),
            error=video_data.get("error")
        )

    def wait_for_video(
        self,
        video_id: str,
        max_wait: int = 600,
        poll_interval: int = 10
    ) -> VideoResult:
        """
        Wait for a video to complete.

        Args:
            video_id: ID of the video
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            VideoResult with final status and video_url
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self.get_video_status(video_id)

            if result.status == "completed":
                return result
            elif result.status == "failed":
                raise Exception(f"Video generation failed: {result.error}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Video {video_id} did not complete within {max_wait} seconds")

    def upload_talking_photo(
        self,
        image_url: str,
        name: str = "Custom Avatar"
    ) -> Avatar:
        """
        Upload a custom talking photo avatar.

        Args:
            image_url: URL to the image file
            name: Name for the talking photo

        Returns:
            Avatar object for the new talking photo
        """
        url = f"{self.BASE_URL}/v2/talking_photo"

        payload = {
            "image_url": image_url,
            "talking_photo_name": name
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        photo_data = data.get("data", {})

        return Avatar(
            avatar_id=photo_data.get("talking_photo_id", ""),
            name=name,
            avatar_type="talking_photo"
        )

    def delete_talking_photo(self, talking_photo_id: str) -> bool:
        """
        Delete a talking photo avatar.

        Args:
            talking_photo_id: ID of the talking photo

        Returns:
            True if successful
        """
        response = requests.delete(
            f"{self.BASE_URL}/v2/talking_photo/{talking_photo_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_remaining_quota(self) -> Dict[str, Any]:
        """
        Get remaining quota/credits.

        Returns:
            Dict with quota information
        """
        response = requests.get(
            f"{self.BASE_URL}/v2/user/remaining_quota",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("data", {})

    def download_video(self, video_url: str, save_path: str) -> str:
        """
        Download a video to local file.

        Args:
            video_url: URL of the video
            save_path: Local path to save

        Returns:
            Path to saved file
        """
        response = requests.get(video_url)
        response.raise_for_status()

        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return save_path

    def create_full_video(
        self,
        avatar_id: str,
        text: str,
        voice_id: str,
        output_path: str,
        aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE,
        avatar_type: AvatarType = AvatarType.AVATAR,
        wait: bool = True
    ) -> VideoResult:
        """
        Create a complete video and optionally wait/download.

        Args:
            avatar_id: Avatar to use
            text: Text to speak
            voice_id: Voice to use
            output_path: Path to save video
            aspect_ratio: Video aspect ratio
            avatar_type: Type of avatar
            wait: Whether to wait for completion

        Returns:
            VideoResult with video URL
        """
        # Create video
        result = self.create_video_from_text(
            avatar_id=avatar_id,
            text=text,
            voice_id=voice_id,
            aspect_ratio=aspect_ratio,
            avatar_type=avatar_type
        )

        if wait:
            result = self.wait_for_video(result.video_id)
            if result.video_url:
                self.download_video(result.video_url, output_path)

        return result
