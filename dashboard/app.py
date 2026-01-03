"""
ADLYTICS - Everything Ads
Complete marketing dashboard with AI-powered agents
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import requests
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    CampaignParser, ClientRegistry, FunnelRegistry, DataAggregator,
    ProductRegistry, WhopAdapter, ClickFunnelsAdapter, HyrosAdapter
)
from dashboard.auth import check_password, logout

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Adlytics - Everything Ads",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not check_password():
    st.stop()

# =============================================================================
# STYLES
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp { background: #0F172A !important; font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 1rem 2rem !important; max-width: 100% !important; }

    /* Sidebar - ALWAYS VISIBLE (no toggle) */
    [data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: 1px solid #334155 !important;
        min-width: 280px !important;
        width: 280px !important;
        transform: none !important;
        position: relative !important;
        visibility: visible !important;
    }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }

    /* Hide sidebar collapse button */
    [data-testid="stSidebar"] button[kind="header"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    button[data-testid="baseButton-header"] { display: none !important; }

    /* Ensure sidebar content is always visible */
    [data-testid="stSidebarContent"] {
        display: flex !important;
        flex-direction: column !important;
    }

    /* Fix sidebar nav content */
    [data-testid="stSidebarNav"] { display: block !important; }
    section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }

    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #F8FAFC !important; font-family: 'Inter', sans-serif !important; }

    /* Logo */
    .logo-container { padding: 16px; margin-bottom: 20px; }
    .logo-main { font-size: 28px; font-weight: 700; }
    .logo-ad { color: #0066FF !important; }
    .logo-lytics { color: #F8FAFC !important; }
    .logo-sub { font-size: 11px; color: #64748B !important; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px; }

    /* KPI Cards */
    .kpi-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .kpi-label { font-size: 12px; color: #94A3B8 !important; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { font-size: 32px; font-weight: 700; color: #F8FAFC !important; }
    .kpi-value.green { color: #10B981 !important; }
    .kpi-value.red { color: #EF4444 !important; }
    .kpi-value.yellow { color: #F59E0B !important; }

    /* Funnel */
    .funnel-container { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
    .funnel-title { font-size: 14px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
    .funnel-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
    .funnel-item { text-align: center; padding: 16px 8px; background: #0F172A; border-radius: 8px; }
    .funnel-item-label { font-size: 11px; color: #94A3B8 !important; margin-bottom: 8px; }
    .funnel-item-value { font-size: 20px; font-weight: 600; color: #F8FAFC !important; }
    .funnel-item-pct { font-size: 24px; font-weight: 700; color: #3B82F6 !important; margin-top: 8px; }

    /* Campaign Table */
    .campaign-table { width: 100%; border-collapse: collapse; }
    .campaign-table th {
        text-align: left; padding: 12px 16px; font-size: 11px; font-weight: 600;
        color: #94A3B8 !important; text-transform: uppercase; border-bottom: 1px solid #334155;
        background: #0F172A;
    }
    .campaign-table td { padding: 16px; border-bottom: 1px solid #1E293B; vertical-align: middle; }
    .campaign-table tr:hover td { background: rgba(59, 130, 246, 0.1); }

    /* Status Badge */
    .status-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500;
    }
    .status-active { background: rgba(16, 185, 129, 0.2); color: #34D399 !important; }
    .status-paused { background: rgba(245, 158, 11, 0.2); color: #FBBF24 !important; }
    .status-off { background: rgba(239, 68, 68, 0.2); color: #F87171 !important; }

    /* Buttons */
    .stButton > button {
        background: #0066FF !important; color: #FFFFFF !important;
        border: none !important; border-radius: 8px !important;
        padding: 8px 16px !important; font-weight: 500 !important;
    }
    .stButton > button:hover { background: #0052CC !important; }

    /* Budget Controls */
    .budget-control { display: flex; align-items: center; gap: 8px; }
    .budget-btn {
        width: 28px; height: 28px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        cursor: pointer; font-weight: 600; transition: all 0.2s;
    }
    .budget-btn-up { background: rgba(16, 185, 129, 0.2); color: #34D399 !important; }
    .budget-btn-down { background: rgba(239, 68, 68, 0.2); color: #F87171 !important; }

    /* AI Analysis Card */
    .ai-card {
        background: #1E293B; border: 1px solid #334155;
        border-radius: 12px; padding: 20px; margin-bottom: 16px;
    }
    .ai-card.critical { border-left: 4px solid #EF4444; }
    .ai-card.warning { border-left: 4px solid #F59E0B; }
    .ai-card.success { border-left: 4px solid #10B981; }
    .ai-card.info { border-left: 4px solid #3B82F6; }
    .ai-card-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .ai-card-body { font-size: 13px; color: #CBD5E1 !important; line-height: 1.6; }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: #1E293B !important; border: 1px solid #334155 !important;
        border-radius: 12px !important; padding: 16px !important;
    }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 11px !important; text-transform: uppercase !important; }
    [data-testid="stMetricValue"] { color: #F8FAFC !important; font-size: 24px !important; font-weight: 600 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #1E293B !important; border-radius: 8px !important; padding: 4px !important; gap: 4px !important; }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #94A3B8 !important;
        border-radius: 6px !important; padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] { background: #0066FF !important; color: #FFFFFF !important; }

    /* Selectbox */
    .stSelectbox > div > div { background: #1E293B !important; border-color: #334155 !important; border-radius: 8px !important; }

    /* Card */
    .card { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 20px; }

    /* Filters bar */
    .filters-bar {
        background: #1E293B; border: 1px solid #334155; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }

    /* Project Selector */
    .project-selector {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 16px;
    }
    .project-selector-label {
        font-size: 10px;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .project-selector-current {
        font-size: 14px;
        font-weight: 600;
        color: #F8FAFC !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tag Filter */
    .tag-filter-container {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
    }
    .tag-chip {
        display: inline-block;
        background: rgba(0, 102, 255, 0.2);
        color: #60A5FA !important;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
        cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    .tag-chip:hover {
        background: rgba(0, 102, 255, 0.4);
        border-color: #0066FF;
    }
    .tag-chip.active {
        background: #0066FF;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'date_range' not in st.session_state:
    st.session_state.date_range = 'last_7d'
if 'custom_start_date' not in st.session_state:
    st.session_state.custom_start_date = date.today() - timedelta(days=7)
if 'custom_end_date' not in st.session_state:
    st.session_state.custom_end_date = date.today() - timedelta(days=1)
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = 'Brazz Scales'
if 'campaign_tag_filter' not in st.session_state:
    st.session_state.campaign_tag_filter = ''

# =============================================================================
# PROJECTS CONFIG
# =============================================================================

PROJECTS = {
    'Brazz Scales': {
        'id': 'brazz-scales',
        'icon': '⚖️',
        'description': 'E-commerce de balanças',
        'default_tags': ['[bsb]', '[bs]', '[brazz]']
    },
    # Adicione novos projetos aqui:
    # 'Novo Projeto': {
    #     'id': 'novo-projeto',
    #     'icon': '🚀',
    #     'description': 'Descrição do projeto',
    #     'default_tags': ['[tag1]', '[tag2]']
    # },
}

# =============================================================================
# API CONFIG
# =============================================================================

API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

def get_credentials():
    try:
        return {
            'meta_token': st.secrets.get("META_ACCESS_TOKEN", ""),
            'meta_account': st.secrets.get("META_AD_ACCOUNT_ID", ""),
            'whop_key': st.secrets.get("WHOP_API_KEY", ""),
            'hyros_key': st.secrets.get("HYROS_API_KEY", "")
        }
    except:
        return {
            'meta_token': os.getenv("META_ACCESS_TOKEN", ""),
            'meta_account': os.getenv("META_AD_ACCOUNT_ID", ""),
            'whop_key': os.getenv("WHOP_API_KEY", ""),
            'hyros_key': os.getenv("HYROS_API_KEY", "")
        }

# =============================================================================
# API FUNCTIONS
# =============================================================================

# All Meta Ads fields we need for comprehensive analysis
META_FIELDS = ','.join([
    'spend', 'impressions', 'reach', 'clicks', 'cpm', 'cpc', 'ctr', 'frequency',
    'actions', 'action_values', 'cost_per_action_type', 'purchase_roas',
    'video_p25_watched_actions', 'video_p50_watched_actions', 'video_p75_watched_actions',
    'video_p100_watched_actions', 'video_play_actions'
])

@st.cache_data(ttl=120)
def fetch_account_insights(account_id: str, token: str, date_preset: str = None, start_date: str = None, end_date: str = None):
    """Fetch account insights with preset or custom date range"""
    if not account_id or not token:
        return None
    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        'fields': META_FIELDS,
        'access_token': token
    }

    # Use custom date range or preset
    if start_date and end_date:
        params['time_range'] = json.dumps({'since': start_date, 'until': end_date})
    else:
        params['date_preset'] = date_preset or 'last_7d'

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'data' in data and data['data']:
            return data['data'][0]
    except:
        pass
    return None

@st.cache_data(ttl=120)
def fetch_campaigns_with_insights(account_id: str, token: str, date_preset: str = None, start_date: str = None, end_date: str = None):
    """Fetch campaigns with insights using preset or custom date range"""
    if not account_id or not token:
        return []
    url = f"{BASE_URL}/{account_id}/campaigns"

    # Build insights clause
    if start_date and end_date:
        insights_clause = f'insights.time_range({{"since":"{start_date}","until":"{end_date}"}}){{{META_FIELDS}}}'
    else:
        preset = date_preset or 'last_7d'
        insights_clause = f'insights.date_preset({preset}){{{META_FIELDS}}}'

    params = {
        'fields': f'id,name,status,effective_status,daily_budget,lifetime_budget,objective,{insights_clause}',
        'limit': 100,
        'access_token': token
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'error' in data:
            return []
        return data.get('data', [])
    except:
        return []

def update_campaign_status(campaign_id: str, status: str, token: str):
    url = f"{BASE_URL}/{campaign_id}"
    params = {'status': status, 'access_token': token}
    try:
        response = requests.post(url, params=params)
        return response.json()
    except:
        return {'error': 'Failed'}

def update_campaign_budget(campaign_id: str, daily_budget: int, token: str):
    url = f"{BASE_URL}/{campaign_id}"
    params = {'daily_budget': daily_budget, 'access_token': token}
    try:
        response = requests.post(url, params=params)
        return response.json()
    except:
        return {'error': 'Failed'}

def extract_action(actions, action_type):
    """Extract action value by type"""
    if not actions:
        return 0
    for a in actions:
        if a.get('action_type') == action_type:
            return float(a.get('value', 0))
    return 0

def extract_cost_per_action(cost_per_action_type, action_type):
    """Extract cost per action by type"""
    if not cost_per_action_type:
        return 0
    for a in cost_per_action_type:
        if a.get('action_type') == action_type:
            return float(a.get('value', 0))
    return 0

def extract_video_views(data, threshold='video_p25'):
    """Extract video views for hook rate calculation"""
    video_actions = data.get(f'{threshold}_watched_actions', [])
    if video_actions:
        for v in video_actions:
            if v.get('action_type') in ['video_view', 'video_p25_watched']:
                return float(v.get('value', 0))
    return 0

def parse_full_metrics(data):
    """Parse all metrics from Meta Ads API response"""
    if not data:
        return {
            'spend': 0, 'revenue': 0, 'profit': 0, 'roas': 0,
            'impressions': 0, 'reach': 0, 'clicks': 0, 'link_clicks': 0,
            'ctr': 0, 'cpc': 0, 'cpm': 0, 'frequency': 0,
            'purchases': 0, 'cpa': 0, 'avg_purchase_value': 0,
            'landing_page_views': 0, 'lp_view_rate': 0,
            'initiate_checkout': 0, 'cost_per_checkout': 0,
            'add_to_cart': 0, 'cost_per_purchase': 0, 'cost_per_result': 0,
            'hook_rate': 0, 'video_plays': 0, 'video_25_views': 0,
            'results': 0
        }

    spend = float(data.get('spend', 0))
    impressions = int(data.get('impressions', 0))

    # Actions
    actions = data.get('actions', [])
    purchases = extract_action(actions, 'purchase')
    landing_page_views = extract_action(actions, 'landing_page_view')
    initiate_checkout = extract_action(actions, 'initiate_checkout')
    add_to_cart = extract_action(actions, 'add_to_cart')
    link_clicks = extract_action(actions, 'link_click')

    # Video actions for hook rate
    video_play_actions = data.get('video_play_actions', [])
    video_plays = 0
    for v in video_play_actions:
        if v.get('action_type') == 'video_view':
            video_plays = float(v.get('value', 0))
            break

    video_25_actions = data.get('video_p25_watched_actions', [])
    video_25_views = 0
    for v in video_25_actions:
        video_25_views = float(v.get('value', 0))
        break

    # Action values (revenue)
    action_values = data.get('action_values', [])
    revenue = extract_action(action_values, 'purchase')

    # Cost per action
    cost_per_action = data.get('cost_per_action_type', [])
    cost_per_checkout = extract_cost_per_action(cost_per_action, 'initiate_checkout')
    cost_per_purchase = extract_cost_per_action(cost_per_action, 'purchase')

    # Calculate derived metrics
    roas = revenue / spend if spend > 0 else 0
    profit = revenue - spend
    cpa = spend / purchases if purchases > 0 else 0
    avg_purchase_value = revenue / purchases if purchases > 0 else 0
    lp_view_rate = (landing_page_views / link_clicks * 100) if link_clicks > 0 else 0
    hook_rate = (video_25_views / impressions * 100) if impressions > 0 else 0

    # Results = purchases for e-commerce
    results = purchases
    cost_per_result = cpa

    return {
        # Spend & Revenue
        'spend': spend,
        'revenue': revenue,
        'profit': profit,
        'roas': roas,
        'avg_purchase_value': avg_purchase_value,

        # Reach & Impressions
        'impressions': impressions,
        'reach': int(data.get('reach', 0)),
        'frequency': float(data.get('frequency', 0)),

        # Clicks
        'clicks': int(data.get('clicks', 0)),
        'link_clicks': int(link_clicks),
        'ctr': float(data.get('ctr', 0)),
        'cpc': float(data.get('cpc', 0)),
        'cpm': float(data.get('cpm', 0)),

        # Video (for Hook Rate)
        'video_plays': int(video_plays),
        'video_25_views': int(video_25_views),
        'hook_rate': hook_rate,

        # Funnel metrics
        'landing_page_views': int(landing_page_views),
        'lp_view_rate': lp_view_rate,
        'initiate_checkout': int(initiate_checkout),
        'cost_per_checkout': cost_per_checkout,
        'add_to_cart': int(add_to_cart),

        # Conversions
        'purchases': int(purchases),
        'results': int(results),
        'cpa': cpa,
        'cost_per_purchase': cost_per_purchase,
        'cost_per_result': cost_per_result
    }

# =============================================================================
# JEREMY HAINES THRESHOLDS & AI ANALYSIS
# =============================================================================

def generate_ai_analysis(metrics_3d, metrics_7d, campaigns):
    """Generate AI analysis based on Jeremy Haines media buying principles"""
    analysis = []

    # THRESHOLDS (Jeremy Haines Style)
    ROAS_KILL = 1.0
    ROAS_WATCH = 1.5
    ROAS_SCALE = 2.0
    CTR_KILL = 0.8
    CTR_GOOD = 1.5
    CPA_THRESHOLD_MULT = 1.5  # 1.5x target CPA = problem
    FREQUENCY_WARNING = 2.5
    FREQUENCY_CRITICAL = 3.5

    # 7-Day Analysis (Primary)
    if metrics_7d['spend'] > 0:
        roas_7d = metrics_7d['roas']
        ctr_7d = metrics_7d['ctr']
        freq_7d = metrics_7d['frequency']
        cpa_7d = metrics_7d['cpa']

        # ROAS Analysis
        if roas_7d < ROAS_KILL:
            analysis.append({
                'type': 'critical',
                'icon': '🚨',
                'title': 'ROAS Crítico - Ação Imediata',
                'body': f'''ROAS de {roas_7d:.2f}x nos últimos 7 dias está abaixo do breakeven.

**Ação Recomendada:**
• Pausar campanhas com ROAS < 1.0x
• Revisar segmentação de público
• Analisar qualidade dos criativos
• Verificar página de destino'''
            })
        elif roas_7d < ROAS_WATCH:
            analysis.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'ROAS em Zona de Atenção',
                'body': f'''ROAS de {roas_7d:.2f}x está na zona de monitoramento (1.0-1.5x).

**Ação Recomendada:**
• Não escalar - manter budget atual
• Testar novos criativos
• Otimizar públicos de melhor performance
• Aguardar mais 3-4 dias para decisão'''
            })
        elif roas_7d >= ROAS_SCALE:
            analysis.append({
                'type': 'success',
                'icon': '🚀',
                'title': 'Performance Saudável - Oportunidade de Scale',
                'body': f'''ROAS de {roas_7d:.2f}x indica campanhas lucrativas.

**Ação Recomendada:**
• Aumentar budget em 20-30% nas top campaigns
• Duplicar adsets vencedores
• Expandir para públicos similares
• Testar novos criativos mantendo winners'''
            })

        # CTR Analysis
        if ctr_7d < CTR_KILL:
            analysis.append({
                'type': 'warning',
                'icon': '📉',
                'title': 'CTR Baixo - Criativos Precisam de Atenção',
                'body': f'''CTR de {ctr_7d:.2f}% está abaixo do ideal (< 0.8%).

**Diagnóstico:**
• Hook dos criativos não está funcionando
• Público pode estar saturado
• Copy não está gerando interesse

**Ação:**
• Testar novos hooks nos primeiros 3 segundos
• Atualizar copies com urgência/escassez
• Testar novos formatos de anúncio'''
            })

        # Frequency Analysis
        if freq_7d >= FREQUENCY_CRITICAL:
            analysis.append({
                'type': 'critical',
                'icon': '🔄',
                'title': 'Frequência Crítica - Fadiga de Audiência',
                'body': f'''Frequência de {freq_7d:.1f}x indica que seu público está saturado.

**Impacto:**
• Aumento de custos
• Queda de CTR e conversões
• Desgaste da marca

**Ação Imediata:**
• Expandir audiência em 50%+
• Adicionar novos interesses
• Criar lookalikes de compradores
• Pausar adsets com freq > 4x'''
            })
        elif freq_7d >= FREQUENCY_WARNING:
            analysis.append({
                'type': 'warning',
                'icon': '👀',
                'title': 'Frequência Elevada - Monitorar',
                'body': f'''Frequência de {freq_7d:.1f}x está se aproximando do limite.

**Ação Preventiva:**
• Preparar novos criativos
• Expandir audiência gradualmente
• Monitorar CPM e CTR diariamente'''
            })

    # 3-Day vs 7-Day Trend Analysis
    if metrics_3d['spend'] > 0 and metrics_7d['spend'] > 0:
        roas_trend = metrics_3d['roas'] - metrics_7d['roas']
        ctr_trend = metrics_3d['ctr'] - metrics_7d['ctr']

        if roas_trend < -0.3:
            analysis.append({
                'type': 'warning',
                'icon': '📊',
                'title': 'Tendência de Queda no ROAS',
                'body': f'''ROAS caiu {abs(roas_trend):.2f}x nos últimos 3 dias vs média de 7 dias.

**Possíveis Causas:**
• Fadiga de criativo
• Aumento de competição
• Mudança no comportamento do público

**Monitorar:** Se continuar caindo por mais 2 dias, reduzir budget em 20%.'''
            })
        elif roas_trend > 0.3:
            analysis.append({
                'type': 'success',
                'icon': '📈',
                'title': 'Tendência de Alta no ROAS',
                'body': f'''ROAS subiu {roas_trend:.2f}x nos últimos 3 dias.

**Indicativo:** Campanhas estão otimizando bem.
**Ação:** Considerar scale moderado de 15-20% se mantiver por mais 2 dias.'''
            })

    # Campaign-specific analysis
    active_camps = [c for c in campaigns if c.get('effective_status') == 'ACTIVE']
    if len(active_camps) > 0:
        analysis.append({
            'type': 'info',
            'icon': '📋',
            'title': f'Resumo: {len(active_camps)} Campanhas Ativas',
            'body': f'''**Métricas Consolidadas (7 dias):**
• Gasto Total: ${metrics_7d["spend"]:,.2f}
• Faturamento: ${metrics_7d["revenue"]:,.2f}
• Lucro: ${metrics_7d["profit"]:,.2f}
• CPA Médio: ${metrics_7d["cpa"]:,.2f}
• {metrics_7d["purchases"]} vendas realizadas'''
        })

    return analysis

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Project Selector (above logo)
    st.markdown('<div class="project-selector-label">PROJETO ATUAL</div>', unsafe_allow_html=True)
    selected_project = st.selectbox(
        "Projeto",
        list(PROJECTS.keys()),
        index=list(PROJECTS.keys()).index(st.session_state.selected_project),
        key="project_selector",
        label_visibility="collapsed"
    )
    if selected_project != st.session_state.selected_project:
        st.session_state.selected_project = selected_project
        st.session_state.campaign_tag_filter = ''  # Reset tag filter on project change
        st.rerun()

    current_project = PROJECTS[st.session_state.selected_project]
    st.markdown(f"""
    <div class="project-selector">
        <div class="project-selector-current">
            {current_project['icon']} {st.session_state.selected_project}
        </div>
        <div style="font-size: 11px; color: #64748B !important; margin-top: 4px;">
            {current_project['description']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div class="logo-container">
        <div class="logo-main">
            <span class="logo-ad">Ad</span><span class="logo-lytics">lytics</span>
        </div>
        <div class="logo-sub">Everything Ads</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### MENU")

    pages = [
        ('dashboard', '🏠', 'Dashboard'),
        ('traffic', '📊', 'Traffic Agent'),
        ('design', '🎨', 'Design Agent'),
        ('video', '🎬', 'Video Editor'),
        ('copy', '✍️', 'Copywriter'),
    ]

    for page_id, icon, title in pages:
        if st.button(f"{icon}  {title}", key=f"nav_{page_id}", use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()

    st.markdown("---")

    if st.button("⚙️  Settings", key="nav_settings", use_container_width=True):
        st.session_state.current_page = 'settings'
        st.rerun()

    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        logout()

    st.markdown("---")
    creds = get_credentials()
    st.markdown("##### STATUS")
    st.markdown(f"{'🟢' if creds['meta_token'] else '🔴'} Meta Ads")
    st.markdown(f"{'🟢' if creds['whop_key'] else '🔴'} Whop")
    st.markdown(f"{'🟢' if creds['hyros_key'] else '🔴'} Hyros")

# =============================================================================
# MAIN CONTENT
# =============================================================================

creds = get_credentials()

# ================== DASHBOARD PAGE ==================
if st.session_state.current_page == 'dashboard':
    st.markdown("## 🏠 Dashboard Principal")

    # Get current project info
    current_project = PROJECTS[st.session_state.selected_project]

    # Filters row
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        date_options = {
            'Hoje': 'today',
            'Ontem': 'yesterday',
            'Últimos 3 dias': 'last_3d',
            'Últimos 7 dias': 'last_7d',
            'Últimos 14 dias': 'last_14d',
            'Últimos 30 dias': 'last_30d'
        }
        selected_date = st.selectbox("Período", list(date_options.keys()), index=3, key="dash_date")
        date_preset = date_options[selected_date]

    with col2:
        # Campaign tag filter
        tag_filter = st.text_input(
            "Filtrar por Tag",
            value=st.session_state.campaign_tag_filter,
            placeholder="Ex: [bsb], [promo], etc.",
            key="dash_tag_filter"
        )
        if tag_filter != st.session_state.campaign_tag_filter:
            st.session_state.campaign_tag_filter = tag_filter

    with col3:
        # Quick tag buttons
        st.markdown('<p style="font-size: 12px; color: #94A3B8; margin-bottom: 4px;">Tags rápidas:</p>', unsafe_allow_html=True)
        tag_cols = st.columns(len(current_project['default_tags']))
        for i, tag in enumerate(current_project['default_tags']):
            with tag_cols[i]:
                is_active = st.session_state.campaign_tag_filter == tag
                if st.button(tag, key=f"quick_tag_{i}", use_container_width=True):
                    if is_active:
                        st.session_state.campaign_tag_filter = ''
                    else:
                        st.session_state.campaign_tag_filter = tag
                    st.rerun()

    with col4:
        if st.button("🔄 Atualizar", use_container_width=True, key="dash_refresh"):
            st.cache_data.clear()
            st.rerun()

    # Show active filter
    if st.session_state.campaign_tag_filter:
        st.markdown(f"""
        <div style="background: rgba(0, 102, 255, 0.1); border: 1px solid #0066FF; border-radius: 8px; padding: 8px 16px; margin-bottom: 16px;">
            <span style="color: #60A5FA;">🏷️ Filtrando por: <strong>{st.session_state.campaign_tag_filter}</strong></span>
            <span style="color: #94A3B8; font-size: 12px; margin-left: 16px;">Apenas campanhas com esta tag serão exibidas</span>
        </div>
        """, unsafe_allow_html=True)

    if creds['meta_token'] and creds['meta_account']:
        # Fetch campaigns to filter by tag
        all_campaigns = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)

        # Filter campaigns by tag if specified
        if st.session_state.campaign_tag_filter:
            tag = st.session_state.campaign_tag_filter.lower()
            filtered_campaigns = [c for c in all_campaigns if tag in c.get('name', '').lower()]
        else:
            filtered_campaigns = all_campaigns

        # Aggregate metrics from filtered campaigns
        def aggregate_campaign_metrics(campaigns):
            """Aggregate metrics from multiple campaigns"""
            total_spend = 0
            total_revenue = 0
            total_impressions = 0
            total_reach = 0
            total_clicks = 0
            total_link_clicks = 0
            total_lp_views = 0
            total_checkouts = 0
            total_purchases = 0
            total_video_25 = 0

            for camp in campaigns:
                camp_data = camp.get('insights', {}).get('data', [{}])[0] if camp.get('insights') else {}
                if camp_data:
                    total_spend += float(camp_data.get('spend', 0))
                    total_impressions += int(camp_data.get('impressions', 0))
                    total_reach += int(camp_data.get('reach', 0))
                    total_clicks += int(camp_data.get('clicks', 0))

                    # Actions
                    actions = camp_data.get('actions', [])
                    for a in actions:
                        at = a.get('action_type')
                        val = float(a.get('value', 0))
                        if at == 'purchase':
                            total_purchases += val
                        elif at == 'landing_page_view':
                            total_lp_views += val
                        elif at == 'initiate_checkout':
                            total_checkouts += val
                        elif at == 'link_click':
                            total_link_clicks += val

                    # Action values
                    action_values = camp_data.get('action_values', [])
                    for av in action_values:
                        if av.get('action_type') == 'purchase':
                            total_revenue += float(av.get('value', 0))

                    # Video views
                    video_25 = camp_data.get('video_p25_watched_actions', [])
                    for v in video_25:
                        total_video_25 += float(v.get('value', 0))

            roas = total_revenue / total_spend if total_spend > 0 else 0
            profit = total_revenue - total_spend
            cpa = total_spend / total_purchases if total_purchases > 0 else 0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            cpc = total_spend / total_clicks if total_clicks > 0 else 0
            frequency = total_impressions / total_reach if total_reach > 0 else 0
            lp_rate = (total_lp_views / total_link_clicks * 100) if total_link_clicks > 0 else 0
            hook_rate = (total_video_25 / total_impressions * 100) if total_impressions > 0 else 0

            return {
                'spend': total_spend,
                'revenue': total_revenue,
                'profit': profit,
                'roas': roas,
                'impressions': int(total_impressions),
                'reach': int(total_reach),
                'clicks': int(total_clicks),
                'link_clicks': int(total_link_clicks),
                'ctr': ctr,
                'cpc': cpc,
                'cpm': cpm,
                'frequency': frequency,
                'purchases': int(total_purchases),
                'cpa': cpa,
                'landing_page_views': int(total_lp_views),
                'lp_view_rate': lp_rate,
                'initiate_checkout': int(total_checkouts),
                'hook_rate': hook_rate,
                'campaign_count': len(campaigns)
            }

        # Get aggregated metrics
        if filtered_campaigns:
            metrics = aggregate_campaign_metrics(filtered_campaigns)
        else:
            # Fallback to account insights if no campaigns match
            insights = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)
            metrics = parse_full_metrics(insights)
            metrics['campaign_count'] = len(all_campaigns)

        # Show campaign count
        if st.session_state.campaign_tag_filter:
            st.markdown(f"**{metrics.get('campaign_count', 0)} campanhas** encontradas com a tag `{st.session_state.campaign_tag_filter}`")

        # KPI Row
        st.markdown("### Resumo")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Faturamento</div>
                <div class="kpi-value green">${metrics['revenue']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Gastos com Anúncios</div>
                <div class="kpi-value">${metrics['spend']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            roas_class = "green" if metrics['roas'] >= 2 else "yellow" if metrics['roas'] >= 1 else "red"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">ROAS</div>
                <div class="kpi-value {roas_class}">{metrics['roas']:.2f}x</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            profit_class = "green" if metrics['profit'] > 0 else "red"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Lucro</div>
                <div class="kpi-value {profit_class}">${metrics['profit']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Funnel and Chart
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("""
            <div class="funnel-container">
                <div class="funnel-title">📊 Funil de Conversão (Meta Ads)</div>
            """, unsafe_allow_html=True)

            clicks = metrics['clicks']
            lp_views = metrics['landing_page_views']
            ic = metrics['initiate_checkout']
            purchases = metrics['purchases']

            # Calculate conversion rates
            lp_rate = (lp_views / clicks * 100) if clicks > 0 else 0
            ic_rate = (ic / lp_views * 100) if lp_views > 0 else 0
            purchase_rate = (purchases / ic * 100) if ic > 0 else 0

            st.markdown(f"""
                <div class="funnel-grid">
                    <div class="funnel-item">
                        <div class="funnel-item-label">Cliques</div>
                        <div class="funnel-item-value">{clicks:,}</div>
                        <div class="funnel-item-pct">100%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Vis. Página</div>
                        <div class="funnel-item-value">{lp_views:,}</div>
                        <div class="funnel-item-pct">{lp_rate:.0f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Init. Checkout</div>
                        <div class="funnel-item-value">{ic:,}</div>
                        <div class="funnel-item-pct">{ic_rate:.0f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Vendas</div>
                        <div class="funnel-item-value">{purchases:,}</div>
                        <div class="funnel-item-pct">{purchase_rate:.0f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">CPA</div>
                        <div class="funnel-item-value">${metrics['cpa']:.2f}</div>
                        <div class="funnel-item-pct">-</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # ROAS Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['roas'],
                number={'suffix': 'x', 'font': {'size': 40, 'color': '#F8FAFC'}},
                title={'text': "ROAS", 'font': {'size': 14, 'color': '#94A3B8'}},
                gauge={
                    'axis': {'range': [0, 5], 'tickcolor': '#475569'},
                    'bar': {'color': "#0066FF"},
                    'bgcolor': "#1E293B",
                    'steps': [
                        {'range': [0, 1], 'color': "rgba(239, 68, 68, 0.3)"},
                        {'range': [1, 2], 'color': "rgba(245, 158, 11, 0.3)"},
                        {'range': [2, 5], 'color': "rgba(16, 185, 129, 0.3)"}
                    ],
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#F8FAFC'},
                height=250,
                margin=dict(t=80, b=0, l=30, r=30)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Additional metrics
        st.markdown("### Métricas Detalhadas")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Impressões", f"{metrics['impressions']:,}")
        col2.metric("Alcance", f"{metrics['reach']:,}")
        col3.metric("Cliques", f"{metrics['clicks']:,}")
        col4.metric("CTR", f"{metrics['ctr']:.2f}%")
        col5.metric("CPC", f"${metrics['cpc']:.2f}")
        col6.metric("Frequência", f"{metrics['frequency']:.2f}")

    else:
        st.warning("Configure META_ACCESS_TOKEN e META_AD_ACCOUNT_ID nos secrets")

# ================== TRAFFIC AGENT PAGE ==================
elif st.session_state.current_page == 'traffic':
    st.markdown("## 📊 Traffic Agent")
    st.markdown("*Análise de campanhas e otimização baseada em dados*")

    if creds['meta_token'] and creds['meta_account']:

        # ========== DATE FILTER (Meta Ads Manager Style) ==========
        st.markdown("### 📅 Período de Análise")

        date_col1, date_col2, date_col3, date_col4 = st.columns([2, 1.5, 1.5, 1])

        with date_col1:
            date_presets = {
                'Hoje': 'today',
                'Ontem': 'yesterday',
                'Últimos 3 dias': 'last_3d',
                'Últimos 7 dias': 'last_7d',
                'Últimos 14 dias': 'last_14d',
                'Últimos 30 dias': 'last_30d',
                'Este mês': 'this_month',
                'Mês passado': 'last_month',
                'Personalizado': 'custom'
            }
            selected_preset = st.selectbox("Período", list(date_presets.keys()), index=3, key="traffic_date_preset")
            date_preset = date_presets[selected_preset]

        # Custom date range inputs
        use_custom_dates = date_preset == 'custom'
        start_date_str = None
        end_date_str = None

        if use_custom_dates:
            with date_col2:
                custom_start = st.date_input("Data inicial", value=st.session_state.custom_start_date, key="traffic_start")
                st.session_state.custom_start_date = custom_start
            with date_col3:
                custom_end = st.date_input("Data final", value=st.session_state.custom_end_date, key="traffic_end")
                st.session_state.custom_end_date = custom_end
            start_date_str = custom_start.strftime('%Y-%m-%d')
            end_date_str = custom_end.strftime('%Y-%m-%d')

        with date_col4:
            if st.button("🔄 Atualizar", key="refresh_traffic", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")

        # Fetch data based on date selection
        if use_custom_dates:
            insights = fetch_account_insights(creds['meta_account'], creds['meta_token'], start_date=start_date_str, end_date=end_date_str)
            campaigns = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], start_date=start_date_str, end_date=end_date_str)
        else:
            insights = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)
            campaigns = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)

        metrics = parse_full_metrics(insights)

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Funil", "📋 Tabela Completa", "📢 Campanhas", "🤖 AI Analysis"])

        # ========== TAB 1: FUNNEL VISUALIZATION ==========
        with tab1:
            st.markdown("### 📊 Funil de Conversão")

            # Main funnel visualization
            st.markdown("""
            <div class="funnel-container">
                <div class="funnel-title">🎯 Jornada do Cliente</div>
            """, unsafe_allow_html=True)

            # Calculate rates
            impr = metrics['impressions']
            reach = metrics['reach']
            clicks = metrics['link_clicks'] if metrics['link_clicks'] > 0 else metrics['clicks']
            lp_views = metrics['landing_page_views']
            checkouts = metrics['initiate_checkout']
            purchases = metrics['purchases']

            click_rate = (clicks / impr * 100) if impr > 0 else 0
            lp_rate = (lp_views / clicks * 100) if clicks > 0 else 0
            checkout_rate = (checkouts / lp_views * 100) if lp_views > 0 else 0
            purchase_rate = (purchases / checkouts * 100) if checkouts > 0 else 0
            overall_cvr = (purchases / clicks * 100) if clicks > 0 else 0

            st.markdown(f"""
                <div class="funnel-grid">
                    <div class="funnel-item">
                        <div class="funnel-item-label">Impressões</div>
                        <div class="funnel-item-value">{impr:,}</div>
                        <div class="funnel-item-pct">100%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Cliques</div>
                        <div class="funnel-item-value">{clicks:,}</div>
                        <div class="funnel-item-pct">{click_rate:.2f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Vis. Página</div>
                        <div class="funnel-item-value">{lp_views:,}</div>
                        <div class="funnel-item-pct">{lp_rate:.1f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Init. Checkout</div>
                        <div class="funnel-item-value">{checkouts:,}</div>
                        <div class="funnel-item-pct">{checkout_rate:.1f}%</div>
                    </div>
                    <div class="funnel-item">
                        <div class="funnel-item-label">Vendas</div>
                        <div class="funnel-item-value">{purchases:,}</div>
                        <div class="funnel-item-pct">{purchase_rate:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Key metrics summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Taxa de Conversão</div>
                    <div class="kpi-value">{overall_cvr:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Hook Rate</div>
                    <div class="kpi-value">{metrics['hook_rate']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Taxa LP View</div>
                    <div class="kpi-value">{metrics['lp_view_rate']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                roas_class = "green" if metrics['roas'] >= 2 else "yellow" if metrics['roas'] >= 1 else "red"
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">ROAS</div>
                    <div class="kpi-value {roas_class}">{metrics['roas']:.2f}x</div>
                </div>
                """, unsafe_allow_html=True)

            # Funnel chart (visual)
            st.markdown("<br>", unsafe_allow_html=True)
            fig = go.Figure(go.Funnel(
                y = ["Impressões", "Cliques", "LP Views", "Checkouts", "Vendas"],
                x = [impr, clicks, lp_views, checkouts, purchases],
                textposition = "inside",
                textinfo = "value+percent previous",
                marker = {
                    "color": ["#3B82F6", "#6366F1", "#8B5CF6", "#A855F7", "#10B981"]
                },
                connector = {"line": {"color": "#334155", "width": 1}}
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#F8FAFC'},
                height=350,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        # ========== TAB 2: COMPLETE METRICS TABLE ==========
        with tab2:
            st.markdown("### 📋 Todas as Métricas")

            # Group metrics by category
            st.markdown("#### 📣 Alcance & Impressões")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Alcance", f"{metrics['reach']:,}")
            col2.metric("Impressões", f"{metrics['impressions']:,}")
            col3.metric("Frequência", f"{metrics['frequency']:.2f}")
            col4.metric("CPM", f"${metrics['cpm']:.2f}")

            st.markdown("---")
            st.markdown("#### 🖱️ Engajamento & Cliques")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Hook Rate", f"{metrics['hook_rate']:.2f}%")
            col2.metric("Cliques no Link", f"{metrics['link_clicks']:,}")
            col3.metric("CTR", f"{metrics['ctr']:.2f}%")
            col4.metric("CPC", f"${metrics['cpc']:.2f}")

            st.markdown("---")
            st.markdown("#### 📄 Landing Page")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Visualizações LP", f"{metrics['landing_page_views']:,}")
            col2.metric("Taxa LP View", f"{metrics['lp_view_rate']:.1f}%")
            col3.metric("Add to Cart", f"{metrics['add_to_cart']:,}")
            col4.metric("-", "-")

            st.markdown("---")
            st.markdown("#### 🛒 Checkout & Vendas")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Checkouts Iniciados", f"{metrics['initiate_checkout']:,}")
            col2.metric("Custo por Checkout", f"${metrics['cost_per_checkout']:.2f}")
            col3.metric("Resultados (Vendas)", f"{metrics['results']:,}")
            col4.metric("Custo por Resultado", f"${metrics['cost_per_result']:.2f}")

            st.markdown("---")
            st.markdown("#### 💰 Financeiro")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Gasto Total", f"${metrics['spend']:,.2f}")
            col2.metric("Valor Conversões", f"${metrics['revenue']:,.2f}")
            col3.metric("Ticket Médio", f"${metrics['avg_purchase_value']:.2f}")
            col4.metric("ROAS", f"{metrics['roas']:.2f}x")
            col5.metric("Lucro", f"${metrics['profit']:,.2f}")

            # Export as DataFrame
            st.markdown("---")
            st.markdown("#### 📥 Exportar Dados")
            metrics_df = pd.DataFrame([{
                'Alcance': metrics['reach'],
                'Impressões': metrics['impressions'],
                'Frequência': round(metrics['frequency'], 2),
                'Hook Rate (%)': round(metrics['hook_rate'], 2),
                'Cliques Link': metrics['link_clicks'],
                'CPM ($)': round(metrics['cpm'], 2),
                'CTR (%)': round(metrics['ctr'], 2),
                'CPC ($)': round(metrics['cpc'], 2),
                'LP Views': metrics['landing_page_views'],
                'Taxa LP View (%)': round(metrics['lp_view_rate'], 1),
                'Checkouts': metrics['initiate_checkout'],
                'Custo/Checkout ($)': round(metrics['cost_per_checkout'], 2),
                'Vendas': metrics['purchases'],
                'Custo/Venda ($)': round(metrics['cost_per_purchase'], 2),
                'Custo/Resultado ($)': round(metrics['cost_per_result'], 2),
                'Gasto Total ($)': round(metrics['spend'], 2),
                'Faturamento ($)': round(metrics['revenue'], 2),
                'Ticket Médio ($)': round(metrics['avg_purchase_value'], 2),
                'ROAS': round(metrics['roas'], 2),
                'Lucro ($)': round(metrics['profit'], 2)
            }])
            st.dataframe(metrics_df.T.rename(columns={0: 'Valor'}), use_container_width=True)

        # ========== TAB 3: CAMPAIGNS TABLE ==========
        with tab3:
            st.markdown("### 📢 Campanhas")

            # Status filter
            col1, col2 = st.columns([3, 1])
            with col1:
                status_filter = st.selectbox("Filtrar por Status", ["Todas", "Ativas", "Pausadas"], key="camp_status_filter")

            # Filter campaigns
            filtered_campaigns = campaigns
            if status_filter == "Ativas":
                filtered_campaigns = [c for c in campaigns if c.get('effective_status') == 'ACTIVE']
            elif status_filter == "Pausadas":
                filtered_campaigns = [c for c in campaigns if c.get('effective_status') == 'PAUSED']

            if filtered_campaigns:
                # Table header
                st.markdown("""
                <table class="campaign-table">
                    <thead>
                        <tr>
                            <th>STATUS</th>
                            <th>CAMPANHA</th>
                            <th>ORÇAMENTO</th>
                            <th>VENDAS</th>
                            <th>CPA</th>
                            <th>GASTOS</th>
                            <th>FATURAMENTO</th>
                            <th>ROAS</th>
                            <th>AÇÕES</th>
                        </tr>
                    </thead>
                </table>
                """, unsafe_allow_html=True)

                for camp in filtered_campaigns:
                    camp_id = camp.get('id', '')
                    name = camp.get('name', 'N/A')
                    status = camp.get('effective_status', 'UNKNOWN')
                    daily_budget = int(camp.get('daily_budget', 0)) / 100

                    # Get campaign insights
                    camp_data = camp.get('insights', {}).get('data', [{}])[0] if camp.get('insights') else {}
                    camp_metrics = parse_full_metrics(camp_data)

                    status_class = "status-active" if status == "ACTIVE" else "status-paused" if status == "PAUSED" else "status-off"
                    status_dot = "🟢" if status == "ACTIVE" else "🟡" if status == "PAUSED" else "🔴"

                    # Campaign row
                    cols = st.columns([1, 3, 1.5, 1, 1, 1, 1.5, 1, 2])

                    with cols[0]:
                        st.markdown(f"<span class='status-badge {status_class}'>{status_dot} {status}</span>", unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"**{name[:40]}**{'...' if len(name) > 40 else ''}")
                    with cols[2]:
                        st.markdown(f"${daily_budget:,.2f}/dia")
                    with cols[3]:
                        st.markdown(f"**{camp_metrics['purchases']}**")
                    with cols[4]:
                        st.markdown(f"${camp_metrics['cpa']:,.2f}")
                    with cols[5]:
                        st.markdown(f"${camp_metrics['spend']:,.2f}")
                    with cols[6]:
                        st.markdown(f"${camp_metrics['revenue']:,.2f}")
                    with cols[7]:
                        roas_color = "#10B981" if camp_metrics['roas'] >= 2 else "#F59E0B" if camp_metrics['roas'] >= 1 else "#EF4444"
                        st.markdown(f"<span style='color: {roas_color}'>{camp_metrics['roas']:.2f}x</span>", unsafe_allow_html=True)
                    with cols[8]:
                        btn_cols = st.columns(3)
                        with btn_cols[0]:
                            if status == "ACTIVE":
                                if st.button("⏸️", key=f"pause_{camp_id}", help="Pausar"):
                                    result = update_campaign_status(camp_id, "PAUSED", creds['meta_token'])
                                    if 'error' not in result:
                                        st.cache_data.clear()
                                        st.rerun()
                            else:
                                if st.button("▶️", key=f"play_{camp_id}", help="Ativar"):
                                    result = update_campaign_status(camp_id, "ACTIVE", creds['meta_token'])
                                    if 'error' not in result:
                                        st.cache_data.clear()
                                        st.rerun()
                        with btn_cols[1]:
                            if st.button("➕", key=f"up_{camp_id}", help="+20% Budget"):
                                new_budget = int(daily_budget * 1.2 * 100)
                                result = update_campaign_budget(camp_id, new_budget, creds['meta_token'])
                                if 'error' not in result:
                                    st.cache_data.clear()
                                    st.rerun()
                        with btn_cols[2]:
                            if st.button("➖", key=f"down_{camp_id}", help="-20% Budget"):
                                new_budget = int(daily_budget * 0.8 * 100)
                                result = update_campaign_budget(camp_id, new_budget, creds['meta_token'])
                                if 'error' not in result:
                                    st.cache_data.clear()
                                    st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhuma campanha encontrada")

        # ========== TAB 4: AI ANALYSIS ==========
        with tab4:
            st.markdown("### 🤖 AI Analysis - Jeremy Haines Framework")
            st.markdown("*Análise baseada em dados de 3 e 7 dias (nunca dados do dia atual)*")

            # Fetch both time periods for AI analysis
            insights_3d = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset='last_3d')
            insights_7d = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset='last_7d')
            campaigns_7d = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], date_preset='last_7d')

            metrics_3d = parse_full_metrics(insights_3d)
            metrics_7d = parse_full_metrics(insights_7d)

            # Comparison cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="card">
                    <h4>📅 Últimos 3 Dias</h4>
                </div>
                """, unsafe_allow_html=True)
                st.metric("ROAS", f"{metrics_3d['roas']:.2f}x")
                st.metric("Gasto", f"${metrics_3d['spend']:,.2f}")
                st.metric("Vendas", f"{metrics_3d['purchases']}")

            with col2:
                st.markdown("""
                <div class="card">
                    <h4>📅 Últimos 7 Dias</h4>
                </div>
                """, unsafe_allow_html=True)
                st.metric("ROAS", f"{metrics_7d['roas']:.2f}x")
                st.metric("Gasto", f"${metrics_7d['spend']:,.2f}")
                st.metric("Vendas", f"{metrics_7d['purchases']}")

            st.markdown("---")
            st.markdown("### 💡 Recomendações da IA")

            analysis = generate_ai_analysis(metrics_3d, metrics_7d, campaigns_7d)

            for item in analysis:
                st.markdown(f"""
                <div class="ai-card {item['type']}">
                    <div class="ai-card-title">{item['icon']} {item['title']}</div>
                    <div class="ai-card-body">{item['body'].replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.warning("Configure META_ACCESS_TOKEN e META_AD_ACCOUNT_ID nos secrets")

# ================== OTHER PAGES (simplified) ==================
elif st.session_state.current_page == 'design':
    st.markdown("## 🎨 Design Agent")
    st.markdown("*Geração de imagens com Leonardo.ai*")
    st.info("Configure LEONARDO_API_KEY para usar este agente")

elif st.session_state.current_page == 'video':
    st.markdown("## 🎬 Video Editor")
    st.markdown("*Vídeos com ElevenLabs + HeyGen*")
    st.info("Configure ELEVENLABS_API_KEY e HEYGEN_API_KEY para usar este agente")

elif st.session_state.current_page == 'copy':
    st.markdown("## ✍️ Copywriter")
    st.markdown("*Geração de copies com IA*")

    product = st.text_input("Produto/Serviço")
    target = st.text_input("Público-alvo")
    if st.button("✍️ Gerar Copy"):
        st.success("Copy gerado! (integração em desenvolvimento)")

elif st.session_state.current_page == 'settings':
    st.markdown("## ⚙️ Settings")
    st.markdown("### Status das Integrações")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Meta Ads:** {'🟢 Conectado' if creds['meta_token'] else '🔴 Não conectado'}")
        st.markdown(f"**Whop:** {'🟢 Conectado' if creds['whop_key'] else '🔴 Não conectado'}")
    with col2:
        st.markdown(f"**Hyros:** {'🟢 Conectado' if creds['hyros_key'] else '🔴 Não conectado'}")

    st.markdown("---")
    st.info("Configure as API keys em Streamlit Cloud → Settings → Secrets")

# Footer
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #64748B !important; font-size: 12px;'>Adlytics v3.2.0 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)
