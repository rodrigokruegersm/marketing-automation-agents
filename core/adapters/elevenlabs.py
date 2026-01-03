"""
ElevenLabs API Adapter
Integration for AI voice cloning and text-to-speech
"""

import os
import time
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class VoiceModel(Enum):
    """ElevenLabs voice models"""
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"  # Best for non-English
    ELEVEN_TURBO_V2 = "eleven_turbo_v2"  # Fastest, English optimized
    ELEVEN_MONOLINGUAL_V1 = "eleven_monolingual_v1"  # Legacy English


class OutputFormat(Enum):
    """Audio output formats"""
    MP3_44100_128 = "mp3_44100_128"
    MP3_44100_192 = "mp3_44100_192"
    PCM_16000 = "pcm_16000"
    PCM_22050 = "pcm_22050"
    PCM_24000 = "pcm_24000"
    PCM_44100 = "pcm_44100"


@dataclass
class Voice:
    """ElevenLabs voice"""
    voice_id: str
    name: str
    category: str  # 'cloned', 'premade', 'professional'
    labels: Dict[str, str] = None
    preview_url: Optional[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


@dataclass
class GeneratedAudio:
    """Result of audio generation"""
    audio_data: bytes
    voice_id: str
    text: str
    model: str
    character_count: int


class ElevenLabsAdapter:
    """
    ElevenLabs API Adapter for voice cloning and text-to-speech.

    Capabilities:
    - List available voices (cloned and premade)
    - Generate speech from text using any voice
    - Clone new voices from audio samples
    - Real-time voice streaming

    Usage:
        adapter = ElevenLabsAdapter(api_key="your_key")

        # List voices
        voices = adapter.list_voices()

        # Generate speech
        audio = adapter.text_to_speech(
            text="Olá, este é um teste de voz clonada.",
            voice_id="your_cloned_voice_id"
        )

        # Save audio
        adapter.save_audio(audio, "output.mp3")
    """

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")

        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def list_voices(self) -> List[Voice]:
        """
        List all available voices (cloned and premade).

        Returns:
            List of Voice objects
        """
        response = requests.get(
            f"{self.BASE_URL}/voices",
            headers=self.headers
        )
        response.raise_for_status()

        data = response.json()
        voices = []

        for v in data.get("voices", []):
            voices.append(Voice(
                voice_id=v.get("voice_id", ""),
                name=v.get("name", ""),
                category=v.get("category", "premade"),
                labels=v.get("labels", {}),
                preview_url=v.get("preview_url")
            ))

        return voices

    def get_voice(self, voice_id: str) -> Voice:
        """
        Get details of a specific voice.

        Args:
            voice_id: The voice ID

        Returns:
            Voice object
        """
        response = requests.get(
            f"{self.BASE_URL}/voices/{voice_id}",
            headers=self.headers
        )
        response.raise_for_status()

        v = response.json()
        return Voice(
            voice_id=v.get("voice_id", ""),
            name=v.get("name", ""),
            category=v.get("category", "premade"),
            labels=v.get("labels", {}),
            preview_url=v.get("preview_url")
        )

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        model: VoiceModel = VoiceModel.ELEVEN_MULTILINGUAL_V2,
        output_format: OutputFormat = OutputFormat.MP3_44100_128,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> GeneratedAudio:
        """
        Generate speech from text using a specific voice.

        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use
            model: Voice model to use
            output_format: Audio output format
            stability: Voice stability (0-1). Lower = more variable
            similarity_boost: How closely to match original voice (0-1)
            style: Style exaggeration (0-1). Higher = more expressive
            use_speaker_boost: Boost similarity to original speaker

        Returns:
            GeneratedAudio with audio bytes
        """
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        params = {"output_format": output_format.value}

        payload = {
            "text": text,
            "model_id": model.value,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }

        response = requests.post(
            url,
            headers=self.headers,
            params=params,
            json=payload
        )
        response.raise_for_status()

        return GeneratedAudio(
            audio_data=response.content,
            voice_id=voice_id,
            text=text,
            model=model.value,
            character_count=len(text)
        )

    def text_to_speech_stream(
        self,
        text: str,
        voice_id: str,
        model: VoiceModel = VoiceModel.ELEVEN_MULTILINGUAL_V2,
        output_format: OutputFormat = OutputFormat.MP3_44100_128
    ):
        """
        Stream speech generation for real-time playback.

        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use
            model: Voice model to use
            output_format: Audio output format

        Yields:
            Audio chunks as bytes
        """
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}/stream"

        params = {"output_format": output_format.value}

        payload = {
            "text": text,
            "model_id": model.value
        }

        response = requests.post(
            url,
            headers=self.headers,
            params=params,
            json=payload,
            stream=True
        )
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    def clone_voice(
        self,
        name: str,
        files: List[str],
        description: str = "",
        labels: Dict[str, str] = None
    ) -> Voice:
        """
        Clone a new voice from audio samples.

        Args:
            name: Name for the cloned voice
            files: List of audio file paths (1-25 files, each up to 10MB)
            description: Description of the voice
            labels: Optional labels for categorization

        Returns:
            Voice object for the new cloned voice
        """
        url = f"{self.BASE_URL}/voices/add"

        # Prepare multipart form data
        files_data = []
        for filepath in files:
            with open(filepath, 'rb') as f:
                files_data.append(
                    ('files', (os.path.basename(filepath), f.read(), 'audio/mpeg'))
                )

        data = {
            'name': name,
            'description': description
        }

        if labels:
            data['labels'] = str(labels)

        # Remove Content-Type header for multipart
        headers = {"xi-api-key": self.api_key}

        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files_data
        )
        response.raise_for_status()

        result = response.json()
        return Voice(
            voice_id=result.get("voice_id", ""),
            name=name,
            category="cloned",
            labels=labels or {}
        )

    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a cloned voice.

        Args:
            voice_id: ID of the voice to delete

        Returns:
            True if successful
        """
        response = requests.delete(
            f"{self.BASE_URL}/voices/{voice_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get user subscription info and usage.

        Returns:
            User info dict with subscription details
        """
        response = requests.get(
            f"{self.BASE_URL}/user",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_character_usage(self) -> Dict[str, int]:
        """
        Get character usage for current billing period.

        Returns:
            Dict with character_count and character_limit
        """
        user_info = self.get_user_info()
        subscription = user_info.get("subscription", {})
        return {
            "character_count": subscription.get("character_count", 0),
            "character_limit": subscription.get("character_limit", 0),
            "remaining": subscription.get("character_limit", 0) - subscription.get("character_count", 0)
        }

    def save_audio(self, audio: GeneratedAudio, filepath: str) -> str:
        """
        Save generated audio to file.

        Args:
            audio: GeneratedAudio object
            filepath: Path to save the audio file

        Returns:
            Path to saved file
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(audio.audio_data)

        return filepath

    def generate_and_save(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        model: VoiceModel = VoiceModel.ELEVEN_MULTILINGUAL_V2
    ) -> str:
        """
        Generate speech and save to file in one step.

        Args:
            text: Text to convert
            voice_id: Voice to use
            output_path: Path to save audio
            model: Voice model

        Returns:
            Path to saved audio file
        """
        audio = self.text_to_speech(text, voice_id, model)
        return self.save_audio(audio, output_path)
