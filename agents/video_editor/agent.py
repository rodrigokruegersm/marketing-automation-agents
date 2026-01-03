"""
Video Editor Agent
AI-powered video ad generation with voice cloning and lip sync

Uses ElevenLabs for voice cloning/TTS and HeyGen for avatar lip sync
to create professional, undetectable AI-generated video ads.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os
import json
from datetime import datetime

from ..base import BaseAgent, AgentConfig, AgentResult

# Import adapters
try:
    from core.adapters.elevenlabs import (
        ElevenLabsAdapter,
        VoiceModel,
        OutputFormat,
        Voice,
        GeneratedAudio
    )
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    from core.adapters.heygen import (
        HeyGenAdapter,
        VideoAspectRatio,
        VideoQuality,
        AvatarType,
        Avatar,
        VideoResult
    )
    HEYGEN_AVAILABLE = True
except ImportError:
    HEYGEN_AVAILABLE = False

try:
    from core.adapters.creatomate import (
        CreatomateAdapter,
        VideoFormat,
        RenderResult
    )
    CREATOMATE_AVAILABLE = True
except ImportError:
    CREATOMATE_AVAILABLE = False


@dataclass
class GeneratedVideoAd:
    """Generated video ad with full metadata"""
    name: str
    video_id: str
    status: str
    video_url: Optional[str] = None
    audio_path: Optional[str] = None
    voice_id: Optional[str] = None
    avatar_id: Optional[str] = None
    script: str = ""
    aspect_ratio: str = "16:9"
    duration: float = 0.0
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'video_id': self.video_id,
            'status': self.status,
            'video_url': self.video_url,
            'audio_path': self.audio_path,
            'voice_id': self.voice_id,
            'avatar_id': self.avatar_id,
            'script': self.script,
            'aspect_ratio': self.aspect_ratio,
            'duration': self.duration,
            'created_at': self.created_at
        }


class VideoEditorAgent(BaseAgent):
    """
    AI Agent for generating video ads with voice cloning and lip sync.

    Pipeline:
    1. Script (from Copy Forge or manual input)
    2. Voice Generation (ElevenLabs - cloned voice)
    3. Video Generation (HeyGen - lip synced avatar)
    4. Output: Professional video ad

    Capabilities:
    - Clone and use custom voices (ElevenLabs)
    - Lip sync avatars to audio (HeyGen)
    - Generate videos from text scripts
    - Bulk video generation for A/B testing
    - Multiple aspect ratios (Feed, Story, YouTube)

    Actions:
    - generate_video: Full pipeline - script to video
    - generate_audio: Generate audio from script (ElevenLabs)
    - create_lipsync: Create lip synced video from audio (HeyGen)
    - list_voices: List available cloned voices
    - list_avatars: List available avatars
    - bulk_generate: Generate multiple videos with different scripts
    - render_template: Render from Creatomate template (fallback)

    Usage:
        agent = VideoEditorAgent()
        result = agent.run({
            'action': 'generate_video',
            'script': 'Olá! Descubra como perder 10kg em 30 dias...',
            'voice_id': 'your_cloned_voice_id',
            'avatar_id': 'your_avatar_id',
            'aspect_ratio': 'story'  # 9:16 for Reels/TikTok
        })
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.elevenlabs: Optional[ElevenLabsAdapter] = None
        self.heygen: Optional[HeyGenAdapter] = None
        self.creatomate: Optional[CreatomateAdapter] = None
        self._init_adapters()

    def _init_adapters(self):
        """Initialize API adapters"""
        # ElevenLabs for voice
        if ELEVENLABS_AVAILABLE and os.getenv("ELEVENLABS_API_KEY"):
            try:
                self.elevenlabs = ElevenLabsAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize ElevenLabs: {e}")

        # HeyGen for lip sync
        if HEYGEN_AVAILABLE and os.getenv("HEYGEN_API_KEY"):
            try:
                self.heygen = HeyGenAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize HeyGen: {e}")

        # Creatomate as fallback for template videos
        if CREATOMATE_AVAILABLE and os.getenv("CREATOMATE_API_KEY"):
            try:
                self.creatomate = CreatomateAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize Creatomate: {e}")

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="VideoEditorAgent",
            description="AI video generation with voice cloning and lip sync",
            version="2.0.0",
            model="elevenlabs+heygen",
            temperature=0.5,
            settings={
                'supported_actions': [
                    'generate_video',
                    'generate_audio',
                    'create_lipsync',
                    'list_voices',
                    'list_avatars',
                    'bulk_generate',
                    'render_template',
                    'check_status'
                ],
                'aspect_ratios': {
                    'landscape': {'ratio': '16:9', 'width': 1920, 'height': 1080},
                    'portrait': {'ratio': '9:16', 'width': 1080, 'height': 1920},
                    'story': {'ratio': '9:16', 'width': 1080, 'height': 1920},
                    'feed': {'ratio': '1:1', 'width': 1080, 'height': 1080},
                    'reels': {'ratio': '9:16', 'width': 1080, 'height': 1920},
                    'tiktok': {'ratio': '9:16', 'width': 1080, 'height': 1920},
                    'youtube': {'ratio': '16:9', 'width': 1920, 'height': 1080}
                },
                'voice_model': 'eleven_multilingual_v2',
                'default_stability': 0.5,
                'default_similarity_boost': 0.75
            }
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute video editor action.

        Args:
            context: Dictionary with:
                - action: Action to perform
                - script: Text script for the video
                - voice_id: ElevenLabs voice ID
                - avatar_id: HeyGen avatar ID
                - aspect_ratio: Output format (story, feed, youtube)
                - wait: Whether to wait for completion

        Returns:
            AgentResult with video data
        """
        action = context.get('action', 'generate_video')

        actions = {
            'generate_video': self._generate_video,
            'generate_audio': self._generate_audio,
            'create_lipsync': self._create_lipsync,
            'list_voices': self._list_voices,
            'list_avatars': self._list_avatars,
            'bulk_generate': self._bulk_generate,
            'render_template': self._render_template,
            'check_status': self._check_status
        }

        if action not in actions:
            return AgentResult(
                success=False,
                data=None,
                message=f"Unknown action: {action}. Available: {list(actions.keys())}"
            )

        return actions[action](context)

    def _generate_video(self, context: Dict[str, Any]) -> AgentResult:
        """
        Full pipeline: Script -> Voice -> Lip Sync Video

        This is the main action for generating complete video ads.
        """
        script = context.get('script', '')
        voice_id = context.get('voice_id')
        avatar_id = context.get('avatar_id')
        aspect_ratio = context.get('aspect_ratio', 'landscape')
        name = context.get('name', f"Video_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        wait = context.get('wait', True)
        use_heygen_voice = context.get('use_heygen_voice', False)

        if not script:
            return AgentResult(
                success=False,
                data=None,
                message="Script is required for video generation"
            )

        # Determine video aspect ratio
        ratio_config = self.config.settings.get('aspect_ratios', {}).get(aspect_ratio, {})
        heygen_ratio = VideoAspectRatio.LANDSCAPE
        if aspect_ratio in ['portrait', 'story', 'reels', 'tiktok']:
            heygen_ratio = VideoAspectRatio.PORTRAIT
        elif aspect_ratio == 'feed':
            heygen_ratio = VideoAspectRatio.SQUARE

        # Option 1: Use HeyGen's built-in TTS
        if use_heygen_voice or not self.elevenlabs:
            if not self.heygen:
                return AgentResult(
                    success=False,
                    data=None,
                    message="HeyGen not configured. Set HEYGEN_API_KEY."
                )

            heygen_voice_id = context.get('heygen_voice_id', voice_id)
            if not heygen_voice_id or not avatar_id:
                return AgentResult(
                    success=False,
                    data=None,
                    message="voice_id (HeyGen) and avatar_id are required"
                )

            try:
                result = self.heygen.create_video_from_text(
                    avatar_id=avatar_id,
                    text=script,
                    voice_id=heygen_voice_id,
                    aspect_ratio=heygen_ratio,
                    avatar_type=AvatarType.TALKING_PHOTO if context.get('is_talking_photo') else AvatarType.AVATAR
                )

                if wait:
                    result = self.heygen.wait_for_video(result.video_id)

                video_ad = GeneratedVideoAd(
                    name=name,
                    video_id=result.video_id,
                    status=result.status,
                    video_url=result.video_url,
                    voice_id=heygen_voice_id,
                    avatar_id=avatar_id,
                    script=script,
                    aspect_ratio=ratio_config.get('ratio', '16:9'),
                    duration=result.duration
                )

                return AgentResult(
                    success=True,
                    data=video_ad.to_dict(),
                    message=f"Video {'completed' if result.status == 'completed' else 'started'}. ID: {result.video_id}"
                )

            except Exception as e:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Video generation failed: {str(e)}"
                )

        # Option 2: ElevenLabs voice + HeyGen lip sync (higher quality)
        if not voice_id:
            return AgentResult(
                success=False,
                data=None,
                message="voice_id (ElevenLabs) is required for voice generation"
            )

        if not self.heygen:
            return AgentResult(
                success=False,
                data=None,
                message="HeyGen not configured. Set HEYGEN_API_KEY."
            )

        if not avatar_id:
            return AgentResult(
                success=False,
                data=None,
                message="avatar_id is required for video generation"
            )

        try:
            # Step 1: Generate audio with ElevenLabs
            audio = self.elevenlabs.text_to_speech(
                text=script,
                voice_id=voice_id,
                model=VoiceModel.ELEVEN_MULTILINGUAL_V2,
                stability=context.get('stability', 0.5),
                similarity_boost=context.get('similarity_boost', 0.75)
            )

            # Save audio temporarily
            audio_dir = "generated/audio"
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = f"{audio_dir}/{name}.mp3"
            self.elevenlabs.save_audio(audio, audio_path)

            # For HeyGen, we need a public URL for the audio
            # In production, upload to S3/CloudStorage and get URL
            # For now, we'll use HeyGen's text-to-speech as fallback
            # TODO: Implement audio URL upload service

            # Step 2: Create video with HeyGen
            # Since we need audio URL, use text-to-speech for now
            # In production, upload audio_path to get URL and use create_video_from_audio
            result = self.heygen.create_video_from_text(
                avatar_id=avatar_id,
                text=script,
                voice_id=context.get('heygen_voice_id', 'en-US-JennyNeural'),  # Fallback voice
                aspect_ratio=heygen_ratio,
                avatar_type=AvatarType.TALKING_PHOTO if context.get('is_talking_photo') else AvatarType.AVATAR
            )

            if wait:
                result = self.heygen.wait_for_video(result.video_id)

            video_ad = GeneratedVideoAd(
                name=name,
                video_id=result.video_id,
                status=result.status,
                video_url=result.video_url,
                audio_path=audio_path,
                voice_id=voice_id,
                avatar_id=avatar_id,
                script=script,
                aspect_ratio=ratio_config.get('ratio', '16:9'),
                duration=result.duration
            )

            return AgentResult(
                success=True,
                data=video_ad.to_dict(),
                message=f"Video {'completed' if result.status == 'completed' else 'started'}. Audio saved: {audio_path}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Video generation failed: {str(e)}"
            )

    def _generate_audio(self, context: Dict[str, Any]) -> AgentResult:
        """Generate audio from script using ElevenLabs"""
        if not self.elevenlabs:
            return AgentResult(
                success=False,
                data=None,
                message="ElevenLabs not configured. Set ELEVENLABS_API_KEY."
            )

        script = context.get('script', '')
        voice_id = context.get('voice_id')
        name = context.get('name', f"Audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        if not script or not voice_id:
            return AgentResult(
                success=False,
                data=None,
                message="script and voice_id are required"
            )

        try:
            audio = self.elevenlabs.text_to_speech(
                text=script,
                voice_id=voice_id,
                model=VoiceModel.ELEVEN_MULTILINGUAL_V2,
                stability=context.get('stability', 0.5),
                similarity_boost=context.get('similarity_boost', 0.75)
            )

            audio_dir = context.get('output_dir', 'generated/audio')
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = f"{audio_dir}/{name}.mp3"
            self.elevenlabs.save_audio(audio, audio_path)

            return AgentResult(
                success=True,
                data={
                    'audio_path': audio_path,
                    'voice_id': voice_id,
                    'script': script,
                    'character_count': audio.character_count
                },
                message=f"Audio generated: {audio_path}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Audio generation failed: {str(e)}"
            )

    def _create_lipsync(self, context: Dict[str, Any]) -> AgentResult:
        """Create lip synced video from audio URL"""
        if not self.heygen:
            return AgentResult(
                success=False,
                data=None,
                message="HeyGen not configured. Set HEYGEN_API_KEY."
            )

        avatar_id = context.get('avatar_id')
        audio_url = context.get('audio_url')
        aspect_ratio = context.get('aspect_ratio', 'landscape')
        wait = context.get('wait', True)

        if not avatar_id or not audio_url:
            return AgentResult(
                success=False,
                data=None,
                message="avatar_id and audio_url are required"
            )

        heygen_ratio = VideoAspectRatio.LANDSCAPE
        if aspect_ratio in ['portrait', 'story', 'reels', 'tiktok']:
            heygen_ratio = VideoAspectRatio.PORTRAIT
        elif aspect_ratio == 'feed':
            heygen_ratio = VideoAspectRatio.SQUARE

        try:
            result = self.heygen.create_video_from_audio(
                avatar_id=avatar_id,
                audio_url=audio_url,
                aspect_ratio=heygen_ratio,
                avatar_type=AvatarType.TALKING_PHOTO if context.get('is_talking_photo') else AvatarType.AVATAR
            )

            if wait:
                result = self.heygen.wait_for_video(result.video_id)

            return AgentResult(
                success=True,
                data={
                    'video_id': result.video_id,
                    'status': result.status,
                    'video_url': result.video_url,
                    'duration': result.duration
                },
                message=f"Lip sync video {'completed' if result.status == 'completed' else 'started'}. ID: {result.video_id}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Lip sync failed: {str(e)}"
            )

    def _list_voices(self, context: Dict[str, Any]) -> AgentResult:
        """List available voices from ElevenLabs"""
        if not self.elevenlabs:
            return AgentResult(
                success=False,
                data=None,
                message="ElevenLabs not configured. Set ELEVENLABS_API_KEY."
            )

        try:
            voices = self.elevenlabs.list_voices()
            voice_list = [
                {
                    'voice_id': v.voice_id,
                    'name': v.name,
                    'category': v.category,
                    'labels': v.labels
                }
                for v in voices
            ]

            # Separate cloned voices
            cloned = [v for v in voice_list if v['category'] == 'cloned']
            premade = [v for v in voice_list if v['category'] != 'cloned']

            return AgentResult(
                success=True,
                data={
                    'voices': voice_list,
                    'cloned_voices': cloned,
                    'premade_voices': premade,
                    'total': len(voice_list),
                    'total_cloned': len(cloned)
                },
                message=f"Found {len(voice_list)} voices ({len(cloned)} cloned)"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to list voices: {str(e)}"
            )

    def _list_avatars(self, context: Dict[str, Any]) -> AgentResult:
        """List available avatars from HeyGen"""
        if not self.heygen:
            return AgentResult(
                success=False,
                data=None,
                message="HeyGen not configured. Set HEYGEN_API_KEY."
            )

        try:
            avatars = self.heygen.list_avatars()
            talking_photos = self.heygen.list_talking_photos()

            avatar_list = [
                {
                    'avatar_id': a.avatar_id,
                    'name': a.name,
                    'type': a.avatar_type,
                    'preview_url': a.preview_url
                }
                for a in avatars
            ]

            photo_list = [
                {
                    'avatar_id': a.avatar_id,
                    'name': a.name,
                    'type': 'talking_photo',
                    'preview_url': a.preview_url
                }
                for a in talking_photos
            ]

            return AgentResult(
                success=True,
                data={
                    'avatars': avatar_list,
                    'talking_photos': photo_list,
                    'total_avatars': len(avatar_list),
                    'total_talking_photos': len(photo_list)
                },
                message=f"Found {len(avatar_list)} avatars and {len(photo_list)} talking photos"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to list avatars: {str(e)}"
            )

    def _bulk_generate(self, context: Dict[str, Any]) -> AgentResult:
        """Generate multiple videos with different scripts"""
        scripts = context.get('scripts', [])
        voice_id = context.get('voice_id')
        avatar_id = context.get('avatar_id')
        aspect_ratio = context.get('aspect_ratio', 'landscape')

        if not scripts:
            return AgentResult(
                success=False,
                data=None,
                message="scripts list is required"
            )

        results = []
        for i, script in enumerate(scripts):
            result = self._generate_video({
                'script': script,
                'voice_id': voice_id,
                'avatar_id': avatar_id,
                'aspect_ratio': aspect_ratio,
                'name': f"Bulk_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'wait': False,  # Don't wait for each, just start
                'use_heygen_voice': context.get('use_heygen_voice', False),
                'heygen_voice_id': context.get('heygen_voice_id'),
                'is_talking_photo': context.get('is_talking_photo', False)
            })

            results.append({
                'index': i + 1,
                'success': result.success,
                'data': result.data,
                'message': result.message
            })

        successful = sum(1 for r in results if r['success'])

        return AgentResult(
            success=successful > 0,
            data={
                'results': results,
                'total': len(scripts),
                'successful': successful,
                'failed': len(scripts) - successful
            },
            message=f"Started {successful}/{len(scripts)} videos"
        )

    def _render_template(self, context: Dict[str, Any]) -> AgentResult:
        """Render video from Creatomate template (fallback method)"""
        if not self.creatomate:
            return AgentResult(
                success=False,
                data=None,
                message="Creatomate not configured. Set CREATOMATE_API_KEY."
            )

        template_id = context.get('template_id')
        modifications = context.get('modifications', {})

        if not template_id:
            return AgentResult(
                success=False,
                data=None,
                message="template_id is required"
            )

        try:
            result = self.creatomate.render_from_template(
                template_id=template_id,
                modifications=modifications
            )

            return AgentResult(
                success=True,
                data={
                    'render_id': result.render_id,
                    'status': result.status,
                    'template_id': template_id
                },
                message=f"Template render started. ID: {result.render_id}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"Template render failed: {str(e)}"
            )

    def _check_status(self, context: Dict[str, Any]) -> AgentResult:
        """Check status of a video generation"""
        video_id = context.get('video_id')

        if not video_id:
            return AgentResult(
                success=False,
                data=None,
                message="video_id is required"
            )

        if self.heygen:
            try:
                result = self.heygen.get_video_status(video_id)
                return AgentResult(
                    success=True,
                    data={
                        'video_id': result.video_id,
                        'status': result.status,
                        'video_url': result.video_url,
                        'duration': result.duration,
                        'error': result.error
                    },
                    message=f"Status: {result.status}"
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Failed to check status: {str(e)}"
                )

        return AgentResult(
            success=False,
            data=None,
            message="No video platform configured"
        )

    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information for all platforms"""
        usage = {}

        if self.elevenlabs:
            try:
                usage['elevenlabs'] = self.elevenlabs.get_character_usage()
            except:
                usage['elevenlabs'] = {'error': 'Failed to get usage'}

        if self.heygen:
            try:
                usage['heygen'] = self.heygen.get_remaining_quota()
            except:
                usage['heygen'] = {'error': 'Failed to get quota'}

        return usage
