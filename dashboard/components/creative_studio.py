"""
Creative Studio Component
Unified interface for ad creation across Design Agent and Video Editor Agent
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

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
        .creative-card-image {
            border-left: 4px solid #F59E0B;
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
        .render-status-rendering {
            background: rgba(59, 130, 246, 0.2);
            color: #3B82F6;
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
        .quick-action-btn {
            background: linear-gradient(135deg, #0066FF 0%, #8B5CF6 100%);
            color: #FFFFFF !important;
            border: none;
            border-radius: 8px;
            padding: 1rem 2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 102, 255, 0.3);
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


def render_quick_create_section():
    """Render the quick create section with unified command interface"""
    st.markdown("""
    <div class="creative-card">
        <h3>Criar Criativo Rapido</h3>
        <p>Use comandos simples para gerar videos e imagens de anuncio</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick command input
    col1, col2 = st.columns([3, 1])
    with col1:
        command = st.text_input(
            "Comando",
            placeholder="Ex: video produto showcase com headline 'Perca 10kg em 30 dias'",
            label_visibility="collapsed"
        )
    with col2:
        create_btn = st.button("Criar", type="primary", use_container_width=True)

    # Command examples
    with st.expander("Exemplos de Comandos"):
        st.markdown("""
        **Videos:**
        - `video produto showcase` - Video de produto basico
        - `video testimonial "Texto do depoimento"` - Video de depoimento
        - `video promo "50% OFF" cta "Compre Agora"` - Video promocional
        - `video text "Seu texto aqui" duration:10` - Video simples com texto

        **Variacoes:**
        - `video variations 3 template:showcase` - Gera 3 variacoes do mesmo template
        - `video bulk headlines:["H1","H2","H3"]` - Gera videos com diferentes headlines

        **Formatos:**
        - `video feed` - Formato 1:1 (Instagram Feed)
        - `video story` - Formato 9:16 (Stories/Reels/TikTok)
        - `video youtube` - Formato 16:9 (YouTube)
        """)

    return command, create_btn


def parse_creative_command(command: str) -> Dict[str, Any]:
    """Parse a creative command into action parameters"""
    command = command.lower().strip()
    params = {
        'type': 'video',
        'action': 'render_video',
        'format': 'feed',
        'modifications': {}
    }

    # Detect type
    if command.startswith('video'):
        params['type'] = 'video'
    elif command.startswith('image') or command.startswith('imagem'):
        params['type'] = 'image'

    # Detect format
    if 'story' in command or 'stories' in command or 'reels' in command:
        params['format'] = 'story'
    elif 'tiktok' in command:
        params['format'] = 'tiktok'
    elif 'youtube' in command:
        params['format'] = 'youtube'
    elif 'feed' in command:
        params['format'] = 'feed'

    # Detect action
    if 'variations' in command:
        params['action'] = 'generate_variations'
        # Extract number of variations
        import re
        match = re.search(r'variations\s+(\d+)', command)
        if match:
            params['variation_count'] = int(match.group(1))
    elif 'bulk' in command:
        params['action'] = 'bulk_render'
    elif 'text' in command:
        params['action'] = 'create_text_video'
        # Extract text in quotes
        import re
        match = re.search(r'"([^"]+)"', command)
        if match:
            params['text'] = match.group(1)

    # Extract template type
    if 'showcase' in command or 'produto' in command:
        params['template_type'] = 'product_showcase'
    elif 'testimonial' in command or 'depoimento' in command:
        params['template_type'] = 'testimonial'
    elif 'promo' in command or 'oferta' in command:
        params['template_type'] = 'promo_offer'

    # Extract quoted strings for modifications
    import re
    quotes = re.findall(r'"([^"]+)"', command)
    if quotes:
        if 'headline' in command:
            params['modifications']['Headline'] = quotes[0]
        elif 'cta' in command and len(quotes) > 1:
            params['modifications']['Headline'] = quotes[0]
            params['modifications']['CTA'] = quotes[1]
        elif params['action'] != 'create_text_video':
            params['modifications']['Headline'] = quotes[0]

    # Extract duration
    match = re.search(r'duration:(\d+)', command)
    if match:
        params['duration'] = float(match.group(1))

    return params


def execute_creative_command(params: Dict[str, Any], client_slug: str = "brez-scales") -> Dict[str, Any]:
    """Execute a parsed creative command"""
    result = {
        'success': False,
        'message': '',
        'data': None
    }

    if not AGENTS_AVAILABLE:
        result['message'] = "Agentes nao disponiveis. Verifique a instalacao."
        return result

    try:
        if params['type'] == 'video':
            agent = VideoEditorAgent()

            # Check if Creatomate is configured
            if not agent.creatomate:
                result['message'] = "CREATOMATE_API_KEY nao configurada. Configure nas variaveis de ambiente."
                return result

            context = {
                'action': params['action'],
                'format': params['format']
            }

            if params['action'] == 'create_text_video':
                context['text'] = params.get('text', 'Seu texto aqui')
                context['duration'] = params.get('duration', 5.0)
                context['format'] = params['format']
            elif params['action'] == 'generate_variations':
                context['template_id'] = params.get('template_id', '')
                context['variations'] = [
                    params.get('modifications', {}).copy()
                    for _ in range(params.get('variation_count', 3))
                ]
            else:
                context['template_id'] = params.get('template_id', '')
                context['modifications'] = params.get('modifications', {})

            agent_result = agent.execute(context)

            if agent_result.success:
                # Save to project knowledge
                creative_data = {
                    'type': 'video',
                    'action': params['action'],
                    'format': params['format'],
                    'template_type': params.get('template_type', 'custom'),
                    'result': agent_result.data,
                    'modifications': params.get('modifications', {})
                }
                filepath = save_creative_to_project(creative_data, client_slug)

                result['success'] = True
                result['message'] = agent_result.message
                result['data'] = agent_result.data
                result['saved_to'] = filepath
            else:
                result['message'] = agent_result.message

        elif params['type'] == 'image':
            agent = DesignAgent()

            context = {
                'action': 'generate',
                'prompt': params.get('modifications', {}).get('Headline', 'Ad creative'),
                'style': 'advertisement',
                'aspect_ratio': '1:1' if params['format'] == 'feed' else '9:16'
            }

            agent_result = agent.execute(context)

            if agent_result.success:
                creative_data = {
                    'type': 'image',
                    'format': params['format'],
                    'result': agent_result.data,
                    'prompt': context['prompt']
                }
                filepath = save_creative_to_project(creative_data, client_slug)

                result['success'] = True
                result['message'] = agent_result.message
                result['data'] = agent_result.data
                result['saved_to'] = filepath
            else:
                result['message'] = agent_result.message

    except Exception as e:
        result['message'] = f"Erro ao executar comando: {str(e)}"

    return result


def render_video_editor_section():
    """Render the video editor section"""
    st.markdown("""
    <div class="creative-card creative-card-video">
        <h3>Editor de Video</h3>
        <p>Geracao de video ads usando Creatomate</p>
    </div>
    """, unsafe_allow_html=True)

    # Template selection
    st.markdown("#### Templates")

    template_options = {
        'product_showcase': 'Showcase de Produto',
        'testimonial': 'Depoimento',
        'promo_offer': 'Oferta Promocional',
        'brand_awareness': 'Awareness',
        'custom': 'Template Personalizado'
    }

    col1, col2 = st.columns(2)
    with col1:
        template_type = st.selectbox(
            "Tipo de Template",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x]
        )
    with col2:
        template_id = st.text_input(
            "Template ID (Creatomate)",
            placeholder="Cole o ID do template do Creatomate"
        )

    # Format selection
    st.markdown("#### Formato de Saida")
    format_cols = st.columns(4)
    formats = {
        'feed': ('1:1', 'Feed'),
        'story': ('9:16', 'Stories/Reels'),
        'tiktok': ('9:16', 'TikTok'),
        'youtube': ('16:9', 'YouTube')
    }

    selected_format = 'feed'
    for idx, (fmt_key, (ratio, label)) in enumerate(formats.items()):
        with format_cols[idx]:
            if st.button(f"{label}\n{ratio}", key=f"fmt_{fmt_key}", use_container_width=True):
                selected_format = fmt_key

    # Dynamic modifications
    st.markdown("#### Modificacoes")
    mod_cols = st.columns(2)
    with mod_cols[0]:
        headline = st.text_input("Headline", placeholder="Seu titulo aqui")
        subheadline = st.text_input("Subheadline", placeholder="Subtitulo opcional")
    with mod_cols[1]:
        cta_text = st.text_input("CTA", placeholder="Ex: Compre Agora")
        video_url = st.text_input("URL do Video/Imagem", placeholder="https://...")

    # Generate button
    if st.button("Gerar Video", type="primary", use_container_width=True):
        if not template_id:
            st.error("Insira o Template ID do Creatomate")
        else:
            with st.spinner("Gerando video..."):
                modifications = {}
                if headline:
                    modifications['Headline'] = headline
                if subheadline:
                    modifications['Subheadline'] = subheadline
                if cta_text:
                    modifications['CTA'] = cta_text
                if video_url:
                    modifications['Video'] = video_url

                params = {
                    'type': 'video',
                    'action': 'render_video',
                    'template_id': template_id,
                    'format': selected_format,
                    'template_type': template_type,
                    'modifications': modifications
                }

                result = execute_creative_command(params)

                if result['success']:
                    st.success(result['message'])
                    if result.get('saved_to'):
                        st.info(f"Salvo em: {result['saved_to']}")
                    if result.get('data', {}).get('render_id'):
                        st.code(f"Render ID: {result['data']['render_id']}")
                else:
                    st.error(result['message'])


def render_variations_section():
    """Render the variations generator section"""
    st.markdown("""
    <div class="creative-card">
        <h3>Gerador de Variacoes</h3>
        <p>Crie multiplas variacoes para testes A/B</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        template_id = st.text_input(
            "Template ID Base",
            placeholder="ID do template para variacoes",
            key="var_template"
        )
    with col2:
        num_variations = st.number_input(
            "Numero de Variacoes",
            min_value=2,
            max_value=10,
            value=3
        )

    # Variation fields
    st.markdown("#### Headlines para Variacao")
    headlines = []
    for i in range(int(num_variations)):
        h = st.text_input(f"Variacao {i+1}", key=f"var_h_{i}", placeholder=f"Headline {i+1}")
        if h:
            headlines.append(h)

    if st.button("Gerar Variacoes", type="primary", use_container_width=True):
        if not template_id:
            st.error("Insira o Template ID")
        elif len(headlines) < 2:
            st.error("Insira pelo menos 2 headlines")
        else:
            with st.spinner(f"Gerando {len(headlines)} variacoes..."):
                params = {
                    'type': 'video',
                    'action': 'generate_variations',
                    'template_id': template_id,
                    'variations': [{'Headline': h} for h in headlines]
                }

                result = execute_creative_command(params)

                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])


def render_project_creatives(client_slug: str = "brez-scales"):
    """Render the project creatives library"""
    st.markdown("""
    <div class="creative-card">
        <h3>Biblioteca de Criativos</h3>
        <p>Criativos gerados e salvos no projeto</p>
    </div>
    """, unsafe_allow_html=True)

    creatives = load_project_creatives(client_slug)

    if not creatives:
        st.info("Nenhum criativo gerado ainda. Use os comandos acima para criar.")
        return

    for creative in creatives[:10]:  # Show last 10
        creative_type = creative.get('type', 'video')
        icon = "" if creative_type == 'video' else ""
        format_name = creative.get('format', 'feed').upper()
        created = creative.get('created_at', '')[:10]

        status = creative.get('result', {}).get('status', 'unknown')
        status_class = {
            'pending': 'render-status-pending',
            'rendering': 'render-status-rendering',
            'succeeded': 'render-status-completed',
            'completed': 'render-status-completed',
            'failed': 'render-status-failed'
        }.get(status, 'render-status-pending')

        render_id = creative.get('result', {}).get('render_id', 'N/A')
        url = creative.get('result', {}).get('url', '')

        st.markdown(f"""
        <div class="template-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.5rem;">{icon}</span>
                    <span class="format-badge">{format_name}</span>
                    <span class="render-status {status_class}">{status.upper()}</span>
                </div>
                <small style="color: #94A3B8;">{created}</small>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #94A3B8;">
                ID: {render_id[:20] if render_id != 'N/A' else 'N/A'}...
            </p>
        </div>
        """, unsafe_allow_html=True)

        if url:
            st.markdown(f"[Baixar Video]({url})")


def render_creative_studio(client_slug: str = "brez-scales"):
    """Main render function for Creative Studio tab"""
    st.markdown(get_creative_studio_styles(), unsafe_allow_html=True)

    st.markdown("## Creative Studio")
    st.caption("Crie videos e imagens de anuncio com um comando")

    # Check API configuration
    creatomate_key = os.getenv("CREATOMATE_API_KEY") or st.secrets.get("CREATOMATE_API_KEY", "")
    if not creatomate_key:
        st.warning("CREATOMATE_API_KEY nao configurada. Configure para gerar videos.")

    # Quick Create Section
    command, create_btn = render_quick_create_section()

    if create_btn and command:
        with st.spinner("Processando comando..."):
            params = parse_creative_command(command)
            result = execute_creative_command(params, client_slug)

            if result['success']:
                st.success(f"Criativo gerado! {result['message']}")
                if result.get('saved_to'):
                    st.info(f"Salvo em: {result['saved_to']}")
            else:
                st.error(result['message'])

    st.markdown("---")

    # Tabs for different sections
    tab_video, tab_variations, tab_library = st.tabs([
        "Editor de Video", "Variacoes A/B", "Biblioteca"
    ])

    with tab_video:
        render_video_editor_section()

    with tab_variations:
        render_variations_section()

    with tab_library:
        render_project_creatives(client_slug)
