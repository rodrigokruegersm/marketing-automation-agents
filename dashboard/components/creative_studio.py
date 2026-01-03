"""
Creative Studio Component
Unified interface for AI video generation with voice cloning and lip sync
Uses ElevenLabs for voice + HeyGen for avatar videos
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import agents
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from agents import VideoEditorAgent, DesignAgent
    from agents.base import AgentResult
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


def get_creative_studio_styles():
    """Get CSS styles for Creative Studio"""
    return """
    <style>
        .creative-card {
            background: #1E293B;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            color: #FFFFFF !important;
        }
        .creative-card h3, .creative-card h4, .creative-card p, .creative-card span {
            color: #FFFFFF !important;
        }
        .creative-card-video {
            border-left: 4px solid #8B5CF6;
        }
        .creative-card-voice {
            border-left: 4px solid #10B981;
        }
        .creative-card-avatar {
            border-left: 4px solid #F59E0B;
        }
        .platform-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }
        .badge-elevenlabs {
            background: rgba(16, 185, 129, 0.2);
            color: #10B981;
        }
        .badge-heygen {
            background: rgba(139, 92, 246, 0.2);
            color: #8B5CF6;
        }
        .template-card {
            background: #0A1628;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.2s;
        }
        .template-card:hover {
            border-color: #0066FF;
            box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
        }
        .render-status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .render-status-pending {
            background: rgba(245, 158, 11, 0.2);
            color: #F59E0B;
        }
        .render-status-completed {
            background: rgba(16, 185, 129, 0.2);
            color: #10B981;
        }
        .render-status-failed {
            background: rgba(239, 68, 68, 0.2);
            color: #EF4444;
        }
        .format-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 500;
            margin-right: 0.25rem;
            background: rgba(0, 102, 255, 0.2);
            color: #0066FF;
        }
        .voice-card {
            background: #0A1628;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.25rem 0;
            cursor: pointer;
        }
        .voice-card:hover {
            border-color: #10B981;
        }
        .voice-card.selected {
            border-color: #10B981;
            background: rgba(16, 185, 129, 0.1);
        }
        .avatar-card {
            background: #0A1628;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 0.75rem;
            text-align: center;
            cursor: pointer;
        }
        .avatar-card:hover {
            border-color: #8B5CF6;
        }
        .avatar-card.selected {
            border-color: #8B5CF6;
            background: rgba(139, 92, 246, 0.1);
        }
    </style>
    """


def save_creative_to_project(creative_data: Dict[str, Any], client_slug: str = "brez-scales"):
    """Save generated creative to project knowledge"""
    creative_dir = f"clients/{client_slug}/creatives"
    os.makedirs(creative_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    creative_type = creative_data.get('type', 'video')
    filename = f"{creative_type}_{timestamp}.json"
    filepath = os.path.join(creative_dir, filename)

    creative_data['created_at'] = datetime.now().isoformat()
    creative_data['client'] = client_slug

    with open(filepath, 'w') as f:
        json.dump(creative_data, f, indent=2)

    return filepath


def load_project_creatives(client_slug: str = "brez-scales") -> list:
    """Load all creatives from project knowledge"""
    creative_dir = f"clients/{client_slug}/creatives"
    creatives = []

    if os.path.exists(creative_dir):
        for filename in os.listdir(creative_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(creative_dir, filename)
                with open(filepath, 'r') as f:
                    creative = json.load(f)
                    creative['filename'] = filename
                    creatives.append(creative)

    return sorted(creatives, key=lambda x: x.get('created_at', ''), reverse=True)


def get_cached_voices():
    """Get cached voices from session state or fetch from API"""
    if 'elevenlabs_voices' not in st.session_state:
        st.session_state.elevenlabs_voices = []
    return st.session_state.elevenlabs_voices


def get_cached_avatars():
    """Get cached avatars from session state"""
    if 'heygen_avatars' not in st.session_state:
        st.session_state.heygen_avatars = []
    if 'heygen_talking_photos' not in st.session_state:
        st.session_state.heygen_talking_photos = []
    return st.session_state.heygen_avatars, st.session_state.heygen_talking_photos


def render_api_status():
    """Render API connection status"""
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") or st.secrets.get("ELEVENLABS_API_KEY", "")
    heygen_key = os.getenv("HEYGEN_API_KEY") or st.secrets.get("HEYGEN_API_KEY", "")

    col1, col2 = st.columns(2)

    with col1:
        if elevenlabs_key:
            st.markdown("""
            <div class="creative-card creative-card-voice" style="padding: 0.75rem;">
                <span>ElevenLabs</span>
                <span class="platform-badge badge-elevenlabs">Conectado</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("ElevenLabs nao configurado")

    with col2:
        if heygen_key:
            st.markdown("""
            <div class="creative-card creative-card-avatar" style="padding: 0.75rem;">
                <span>HeyGen</span>
                <span class="platform-badge badge-heygen">Conectado</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("HeyGen nao configurado")

    return bool(elevenlabs_key), bool(heygen_key)


def render_voice_selector():
    """Render voice selection interface"""
    st.markdown("### Voz Clonada")
    st.caption("Selecione a voz clonada para o video")

    if not AGENTS_AVAILABLE:
        st.error("Agentes nao disponiveis")
        return None

    # Load voices button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Carregar Vozes", use_container_width=True):
            with st.spinner("Carregando vozes..."):
                try:
                    agent = VideoEditorAgent()
                    result = agent.execute({'action': 'list_voices'})
                    if result.success:
                        st.session_state.elevenlabs_voices = result.data.get('voices', [])
                        st.success(f"Carregadas {len(st.session_state.elevenlabs_voices)} vozes")
                    else:
                        st.error(result.message)
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

    voices = get_cached_voices()

    if not voices:
        st.info("Clique em 'Carregar Vozes' para ver suas vozes clonadas")
        # Manual voice ID input
        voice_id = st.text_input(
            "Ou insira o Voice ID manualmente",
            placeholder="Cole o ID da voz do ElevenLabs"
        )
        return voice_id

    # Separate cloned vs premade
    cloned = [v for v in voices if v.get('category') == 'cloned']
    premade = [v for v in voices if v.get('category') != 'cloned']

    if cloned:
        st.markdown("**Suas Vozes Clonadas:**")
        selected_voice = st.selectbox(
            "Selecione a voz",
            options=[v['voice_id'] for v in cloned],
            format_func=lambda x: next((v['name'] for v in cloned if v['voice_id'] == x), x),
            label_visibility="collapsed"
        )
        return selected_voice

    st.warning("Nenhuma voz clonada encontrada. Clone uma voz no ElevenLabs primeiro.")
    return None


def render_avatar_selector():
    """Render avatar selection interface"""
    st.markdown("### Avatar / Talking Photo")
    st.caption("Selecione o avatar para lip sync")

    if not AGENTS_AVAILABLE:
        st.error("Agentes nao disponiveis")
        return None, False

    # Load avatars button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Carregar Avatares", use_container_width=True):
            with st.spinner("Carregando avatares..."):
                try:
                    agent = VideoEditorAgent()
                    result = agent.execute({'action': 'list_avatars'})
                    if result.success:
                        st.session_state.heygen_avatars = result.data.get('avatars', [])
                        st.session_state.heygen_talking_photos = result.data.get('talking_photos', [])
                        total = len(st.session_state.heygen_avatars) + len(st.session_state.heygen_talking_photos)
                        st.success(f"Carregados {total} avatares")
                    else:
                        st.error(result.message)
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

    avatars, talking_photos = get_cached_avatars()

    if not avatars and not talking_photos:
        st.info("Clique em 'Carregar Avatares' para ver seus avatares")
        # Manual avatar ID input
        avatar_id = st.text_input(
            "Ou insira o Avatar ID manualmente",
            placeholder="Cole o ID do avatar do HeyGen"
        )
        is_talking_photo = st.checkbox("E uma Talking Photo?")
        return avatar_id, is_talking_photo

    # Show talking photos first (custom)
    is_talking_photo = False
    selected_avatar = None

    if talking_photos:
        st.markdown("**Suas Talking Photos (Custom):**")
        tp_options = [(tp['avatar_id'], tp['name']) for tp in talking_photos]
        selected_tp = st.selectbox(
            "Talking Photo",
            options=[tp[0] for tp in tp_options],
            format_func=lambda x: next((tp[1] for tp in tp_options if tp[0] == x), x),
            key="tp_select"
        )
        if selected_tp:
            selected_avatar = selected_tp
            is_talking_photo = True

    if avatars and not is_talking_photo:
        st.markdown("**Avatares HeyGen:**")
        av_options = [(av['avatar_id'], av['name']) for av in avatars]
        selected_av = st.selectbox(
            "Avatar",
            options=[av[0] for av in av_options],
            format_func=lambda x: next((av[1] for av in av_options if av[0] == x), x),
            key="av_select"
        )
        if selected_av:
            selected_avatar = selected_av
            is_talking_photo = False

    return selected_avatar, is_talking_photo


def render_video_generator(client_slug: str = "brez-scales"):
    """Render the main video generator interface"""
    st.markdown("""
    <div class="creative-card creative-card-video">
        <h3>Gerador de Video Ads</h3>
        <p>Crie videos com voz clonada e lip sync usando ElevenLabs + HeyGen</p>
    </div>
    """, unsafe_allow_html=True)

    # Check API status
    has_elevenlabs, has_heygen = render_api_status()

    if not has_elevenlabs or not has_heygen:
        st.error("Configure ELEVENLABS_API_KEY e HEYGEN_API_KEY para gerar videos")
        return

    st.markdown("---")

    # Script input
    st.markdown("### Script do Anuncio")
    script = st.text_area(
        "Script",
        placeholder="Digite o script que o avatar vai falar...\n\nEx: Ola! Voce sabia que pode perder ate 10kg em apenas 30 dias? Com nosso metodo exclusivo...",
        height=150,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)

    with col1:
        voice_id = render_voice_selector()

    with col2:
        avatar_id, is_talking_photo = render_avatar_selector()

    st.markdown("---")

    # Format selection
    st.markdown("### Formato de Saida")
    format_cols = st.columns(4)
    formats = {
        'story': ('9:16', 'Stories/Reels/TikTok'),
        'feed': ('1:1', 'Feed'),
        'youtube': ('16:9', 'YouTube'),
        'landscape': ('16:9', 'Landscape')
    }

    if 'selected_format' not in st.session_state:
        st.session_state.selected_format = 'story'

    for idx, (fmt_key, (ratio, label)) in enumerate(formats.items()):
        with format_cols[idx]:
            btn_type = "primary" if st.session_state.selected_format == fmt_key else "secondary"
            if st.button(f"{label}\n{ratio}", key=f"fmt_{fmt_key}", use_container_width=True, type=btn_type):
                st.session_state.selected_format = fmt_key
                st.rerun()

    st.markdown("---")

    # Advanced options
    with st.expander("Opcoes Avancadas"):
        col1, col2 = st.columns(2)
        with col1:
            stability = st.slider("Estabilidade da Voz", 0.0, 1.0, 0.5, 0.1)
            similarity = st.slider("Similaridade", 0.0, 1.0, 0.75, 0.05)
        with col2:
            wait_for_completion = st.checkbox("Aguardar conclusao", value=True)
            use_heygen_voice = st.checkbox("Usar voz do HeyGen (ao inves de ElevenLabs)")

    # Generate button
    if st.button("Gerar Video", type="primary", use_container_width=True):
        if not script:
            st.error("Digite o script do anuncio")
        elif not voice_id and not use_heygen_voice:
            st.error("Selecione uma voz clonada")
        elif not avatar_id:
            st.error("Selecione um avatar")
        else:
            with st.spinner("Gerando video... Isso pode levar alguns minutos."):
                try:
                    agent = VideoEditorAgent()
                    result = agent.execute({
                        'action': 'generate_video',
                        'script': script,
                        'voice_id': voice_id,
                        'avatar_id': avatar_id,
                        'aspect_ratio': st.session_state.selected_format,
                        'is_talking_photo': is_talking_photo,
                        'stability': stability,
                        'similarity_boost': similarity,
                        'wait': wait_for_completion,
                        'use_heygen_voice': use_heygen_voice
                    })

                    if result.success:
                        st.success(f"Video gerado! {result.message}")

                        # Save to project
                        creative_data = {
                            'type': 'video',
                            'platform': 'heygen',
                            'voice_platform': 'elevenlabs' if not use_heygen_voice else 'heygen',
                            'script': script,
                            'voice_id': voice_id,
                            'avatar_id': avatar_id,
                            'format': st.session_state.selected_format,
                            'result': result.data
                        }
                        filepath = save_creative_to_project(creative_data, client_slug)
                        st.info(f"Salvo em: {filepath}")

                        # Show video URL if available
                        if result.data and result.data.get('video_url'):
                            st.video(result.data['video_url'])
                            st.markdown(f"[Baixar Video]({result.data['video_url']})")
                    else:
                        st.error(f"Erro: {result.message}")

                except Exception as e:
                    st.error(f"Erro ao gerar video: {str(e)}")


def render_bulk_generator(client_slug: str = "brez-scales"):
    """Render bulk video generator for A/B testing"""
    st.markdown("""
    <div class="creative-card">
        <h3>Geracao em Lote (A/B Testing)</h3>
        <p>Gere multiplos videos com diferentes scripts para testar</p>
    </div>
    """, unsafe_allow_html=True)

    # Voice and avatar selection
    col1, col2 = st.columns(2)

    with col1:
        voice_id = st.text_input(
            "Voice ID (ElevenLabs)",
            placeholder="ID da voz clonada",
            key="bulk_voice"
        )
    with col2:
        avatar_id = st.text_input(
            "Avatar ID (HeyGen)",
            placeholder="ID do avatar",
            key="bulk_avatar"
        )

    is_talking_photo = st.checkbox("E uma Talking Photo?", key="bulk_tp")

    # Scripts input
    st.markdown("### Scripts (um por linha)")
    scripts_text = st.text_area(
        "Scripts",
        placeholder="Script 1: Ola! Descubra como...\nScript 2: Voce esta cansado de...\nScript 3: Finalmente um metodo que...",
        height=200,
        label_visibility="collapsed"
    )

    aspect_ratio = st.selectbox(
        "Formato",
        options=['story', 'feed', 'youtube', 'landscape'],
        format_func=lambda x: {'story': 'Stories/Reels (9:16)', 'feed': 'Feed (1:1)', 'youtube': 'YouTube (16:9)', 'landscape': 'Landscape (16:9)'}.get(x, x)
    )

    if st.button("Gerar Todos os Videos", type="primary", use_container_width=True):
        if not voice_id or not avatar_id:
            st.error("Voice ID e Avatar ID sao obrigatorios")
        elif not scripts_text.strip():
            st.error("Insira pelo menos um script")
        else:
            scripts = [s.strip() for s in scripts_text.strip().split('\n') if s.strip()]
            st.info(f"Gerando {len(scripts)} videos...")

            with st.spinner(f"Gerando {len(scripts)} videos..."):
                try:
                    agent = VideoEditorAgent()
                    result = agent.execute({
                        'action': 'bulk_generate',
                        'scripts': scripts,
                        'voice_id': voice_id,
                        'avatar_id': avatar_id,
                        'aspect_ratio': aspect_ratio,
                        'is_talking_photo': is_talking_photo
                    })

                    if result.success:
                        st.success(result.message)

                        # Show results
                        for r in result.data.get('results', []):
                            if r['success']:
                                st.success(f"Video {r['index']}: {r['message']}")
                            else:
                                st.error(f"Video {r['index']}: {r['message']}")
                    else:
                        st.error(result.message)

                except Exception as e:
                    st.error(f"Erro: {str(e)}")


def render_project_creatives(client_slug: str = "brez-scales"):
    """Render the project creatives library"""
    st.markdown("""
    <div class="creative-card">
        <h3>Biblioteca de Criativos</h3>
        <p>Videos gerados e salvos no projeto</p>
    </div>
    """, unsafe_allow_html=True)

    creatives = load_project_creatives(client_slug)

    if not creatives:
        st.info("Nenhum criativo gerado ainda. Use o gerador acima para criar.")
        return

    for creative in creatives[:10]:
        creative_type = creative.get('type', 'video')
        platform = creative.get('platform', 'unknown')
        format_name = creative.get('format', 'feed').upper()
        created = creative.get('created_at', '')[:10]
        script_preview = creative.get('script', '')[:50] + '...' if creative.get('script') else 'N/A'

        status = creative.get('result', {}).get('status', 'unknown')
        status_class = {
            'pending': 'render-status-pending',
            'completed': 'render-status-completed',
            'failed': 'render-status-failed'
        }.get(status, 'render-status-pending')

        video_id = creative.get('result', {}).get('video_id', 'N/A')
        video_url = creative.get('result', {}).get('video_url', '')

        st.markdown(f"""
        <div class="template-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="format-badge">{format_name}</span>
                    <span class="platform-badge badge-heygen">{platform.upper()}</span>
                    <span class="render-status {status_class}">{status.upper()}</span>
                </div>
                <small style="color: #94A3B8;">{created}</small>
            </div>
            <p style="margin: 0.5rem 0; font-size: 0.85rem; color: #CBD5E1;">{script_preview}</p>
            <small style="color: #64748B;">ID: {video_id[:20] if video_id != 'N/A' else 'N/A'}...</small>
        </div>
        """, unsafe_allow_html=True)

        if video_url:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"[Baixar]({video_url})")


def render_creative_studio(client_slug: str = "brez-scales"):
    """Main render function for Creative Studio tab"""
    st.markdown(get_creative_studio_styles(), unsafe_allow_html=True)

    st.markdown("## Creative Studio")
    st.caption("Gere videos com voz clonada e lip sync - ElevenLabs + HeyGen")

    # Tabs for different sections
    tab_generate, tab_bulk, tab_library = st.tabs([
        "Gerar Video", "Geracao em Lote", "Biblioteca"
    ])

    with tab_generate:
        render_video_generator(client_slug)

    with tab_bulk:
        render_bulk_generator(client_slug)

    with tab_library:
        render_project_creatives(client_slug)
