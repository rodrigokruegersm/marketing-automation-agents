"""
MEDIA BUYING COMMAND CENTER
Central de controle para gestao de trafego pago com IA
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Media Buying Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# STYLES
# =============================================================================

st.markdown("""
<style>
    /* Base */
    .stApp { background-color: #0F0F1A !important; }
    .block-container { padding: 1rem 2rem !important; max-width: 1600px !important; }

    /* Typography */
    h1, h2, h3, p, span, div, label { color: #FFFFFF !important; }
    h1 { font-size: 2rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; margin-top: 1.5rem !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; }

    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1A1A2E 0%, #16162A 100%) !important;
        border: 1px solid #2D2D44 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricLabel"] { color: #8B8BA3 !important; font-size: 0.75rem !important; text-transform: uppercase !important; }
    [data-testid="stMetricLabel"] * { color: #8B8BA3 !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] * { color: #FFFFFF !important; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
    }

    /* Action Buttons */
    .action-btn-success > button { background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; }
    .action-btn-danger > button { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important; }
    .action-btn-warning > button { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; }

    /* Cards */
    .command-card {
        background: linear-gradient(135deg, #1A1A2E 0%, #16162A 100%);
        border: 1px solid #2D2D44;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* AI Suggestion Box */
    .ai-suggestion {
        background: linear-gradient(135deg, #1E3A5F 0%, #1A2744 100%);
        border: 1px solid #3B82F6;
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    .ai-suggestion-critical {
        background: linear-gradient(135deg, #5F1E1E 0%, #441A1A 100%);
        border-color: #EF4444;
    }
    .ai-suggestion-opportunity {
        background: linear-gradient(135deg, #1E5F2F 0%, #1A4424 100%);
        border-color: #10B981;
    }

    /* Campaign Row */
    .campaign-row {
        background: #1A1A2E;
        border: 1px solid #2D2D44;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Status Badges */
    .status-active { color: #10B981 !important; }
    .status-paused { color: #F59E0B !important; }
    .status-error { color: #EF4444 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #12121F !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Selectbox */
    .stSelectbox > div > div { background: #1A1A2E !important; border-color: #2D2D44 !important; }
    .stSelectbox * { color: #FFFFFF !important; }

    /* Number Input */
    .stNumberInput > div > div > input { background: #1A1A2E !important; color: #FFFFFF !important; border-color: #2D2D44 !important; }

    /* Expander */
    .streamlit-expanderHeader { background: #1A1A2E !important; border: 1px solid #2D2D44 !important; border-radius: 8px !important; }
    .streamlit-expanderContent { background: #16162A !important; border: 1px solid #2D2D44 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 0.5rem !important; }
    .stTabs [data-baseweb="tab"] { background: #1A1A2E !important; border-radius: 8px !important; color: #8B8BA3 !important; }
    .stTabs [aria-selected="true"] { background: #6366F1 !important; color: white !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden !important; }

    /* Alerts */
    .stAlert { background: #1A1A2E !important; border: 1px solid #2D2D44 !important; }
    .stAlert * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Try to load from Streamlit secrets first (for cloud), then env vars
try:
    META_ACCESS_TOKEN = st.secrets["META_ACCESS_TOKEN"]
    META_AD_ACCOUNT_ID = st.secrets["META_AD_ACCOUNT_ID"]
except:
    META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', '')
    META_AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID', '')

API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

# =============================================================================
# API FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def fetch_account_insights(date_preset='last_3d'):
    """Fetch account-level insights"""
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/insights"
    params = {
        'fields': 'spend,impressions,reach,frequency,cpm,clicks,cpc,ctr,actions,action_values,cost_per_action_type,purchase_roas',
        'date_preset': date_preset,
        'access_token': META_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('data', [{}])[0] if 'data' in data else None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_campaigns():
    """Fetch all campaigns with their status and metrics"""
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status,daily_budget,lifetime_budget,objective,insights.date_preset(last_3d){spend,impressions,clicks,actions,action_values,purchase_roas}',
        'limit': 50,
        'access_token': META_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching campaigns: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_adsets(campaign_id=None):
    """Fetch ad sets"""
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/adsets"
    params = {
        'fields': 'id,name,status,effective_status,daily_budget,campaign_id,targeting,insights.date_preset(last_3d){spend,impressions,clicks,actions,action_values,ctr,cpc}',
        'limit': 100,
        'access_token': META_ACCESS_TOKEN
    }
    if campaign_id:
        params['filtering'] = json.dumps([{'field': 'campaign.id', 'operator': 'EQUAL', 'value': campaign_id}])
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        return []

def update_campaign_status(campaign_id, status):
    """Update campaign status (ACTIVE/PAUSED)"""
    url = f"{BASE_URL}/{campaign_id}"
    params = {
        'status': status,
        'access_token': META_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def update_adset_status(adset_id, status):
    """Update ad set status"""
    url = f"{BASE_URL}/{adset_id}"
    params = {
        'status': status,
        'access_token': META_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def update_budget(entity_id, budget_cents, budget_type='daily_budget'):
    """Update budget (in cents)"""
    url = f"{BASE_URL}/{entity_id}"
    params = {
        budget_type: budget_cents,
        'access_token': META_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_action_value(actions, action_type):
    """Extract value from actions array"""
    if not actions:
        return 0
    for action in actions:
        if action.get('action_type') == action_type:
            return float(action.get('value', 0))
    return 0

def parse_metrics(raw_data):
    """Parse raw API data into metrics dict"""
    if not raw_data:
        return None

    actions = raw_data.get('actions', [])
    action_values = raw_data.get('action_values', [])
    cost_per_action = raw_data.get('cost_per_action_type', [])

    spend = float(raw_data.get('spend', 0))
    revenue = extract_action_value(action_values, 'purchase')
    purchases = extract_action_value(actions, 'purchase')

    return {
        'spend': spend,
        'revenue': revenue,
        'profit': revenue - spend,
        'roas': float(raw_data.get('purchase_roas', [{}])[0].get('value', 0)) if raw_data.get('purchase_roas') else (revenue / spend if spend > 0 else 0),
        'impressions': int(raw_data.get('impressions', 0)),
        'reach': int(raw_data.get('reach', 0)),
        'frequency': float(raw_data.get('frequency', 0)),
        'clicks': int(raw_data.get('clicks', 0)),
        'ctr': float(raw_data.get('ctr', 0)),
        'cpc': float(raw_data.get('cpc', 0)),
        'cpm': float(raw_data.get('cpm', 0)),
        'purchases': purchases,
        'cpp': extract_action_value(cost_per_action, 'purchase'),
        'link_clicks': extract_action_value(actions, 'link_click'),
        'lp_views': extract_action_value(actions, 'landing_page_view'),
        'checkouts': extract_action_value(actions, 'initiate_checkout'),
    }

def generate_ai_suggestions(metrics, campaigns):
    """Generate AI-powered optimization suggestions"""
    suggestions = []

    if not metrics:
        return suggestions

    # ROAS Analysis
    if metrics['roas'] < 1.5:
        suggestions.append({
            'type': 'critical',
            'icon': '🚨',
            'title': 'ROAS Critico - Acao Imediata',
            'message': f"ROAS atual: {metrics['roas']:.2f}x (abaixo de 1.5x). Pausar campanhas de baixo desempenho e revisar targeting.",
            'action': 'pause_low_performers',
            'priority': 1
        })
    elif metrics['roas'] >= 2.5:
        suggestions.append({
            'type': 'opportunity',
            'icon': '🚀',
            'title': 'Oportunidade de Escala',
            'message': f"ROAS forte: {metrics['roas']:.2f}x. Considere aumentar budget em 20-30% nas campanhas top performers.",
            'action': 'scale_budget',
            'priority': 2
        })

    # Frequency Analysis
    if metrics['frequency'] > 3:
        suggestions.append({
            'type': 'critical',
            'icon': '🔄',
            'title': 'Frequencia Alta - Fadiga de Criativo',
            'message': f"Frequencia: {metrics['frequency']:.2f}. Audiencia saturada. Subir novos criativos ou expandir publico.",
            'action': 'new_creatives',
            'priority': 1
        })
    elif metrics['frequency'] > 2.5:
        suggestions.append({
            'type': 'warning',
            'icon': '⚠️',
            'title': 'Monitorar Frequencia',
            'message': f"Frequencia: {metrics['frequency']:.2f}. Preparar novos criativos para os proximos dias.",
            'action': 'prepare_creatives',
            'priority': 3
        })

    # CPP Analysis
    if metrics['cpp'] > 25:
        suggestions.append({
            'type': 'critical',
            'icon': '💸',
            'title': 'CPP Muito Alto',
            'message': f"Custo por compra: ${metrics['cpp']:.2f}. Revisar ad sets com CPP acima de $20.",
            'action': 'review_cpp',
            'priority': 1
        })
    elif metrics['cpp'] <= 12:
        suggestions.append({
            'type': 'opportunity',
            'icon': '💎',
            'title': 'CPP Excelente',
            'message': f"CPP: ${metrics['cpp']:.2f}. Identificar os ad sets com melhor CPP e aumentar budget.",
            'action': 'scale_low_cpp',
            'priority': 2
        })

    # CTR Analysis
    if metrics['ctr'] < 1:
        suggestions.append({
            'type': 'warning',
            'icon': '👆',
            'title': 'CTR Baixo',
            'message': f"CTR: {metrics['ctr']:.2f}%. Testar novos hooks nos primeiros 3 segundos dos videos.",
            'action': 'improve_ctr',
            'priority': 3
        })
    elif metrics['ctr'] >= 3:
        suggestions.append({
            'type': 'opportunity',
            'icon': '🎯',
            'title': 'CTR Alto',
            'message': f"CTR: {metrics['ctr']:.2f}%. Criativos performando bem. Duplicar para novos publicos.",
            'action': 'duplicate_ads',
            'priority': 3
        })

    # Funnel Analysis
    if metrics['lp_views'] > 0 and metrics['checkouts'] > 0:
        lp_to_checkout = (metrics['checkouts'] / metrics['lp_views']) * 100
        if lp_to_checkout < 5:
            suggestions.append({
                'type': 'warning',
                'icon': '📊',
                'title': 'Conversao LP Baixa',
                'message': f"Taxa LP->Checkout: {lp_to_checkout:.1f}%. Problema na landing page ou oferta.",
                'action': 'review_lp',
                'priority': 2
            })

    if metrics['checkouts'] > 0 and metrics['purchases'] > 0:
        checkout_to_purchase = (metrics['purchases'] / metrics['checkouts']) * 100
        if checkout_to_purchase < 50:
            suggestions.append({
                'type': 'warning',
                'icon': '🛒',
                'title': 'Abandono de Checkout Alto',
                'message': f"Taxa Checkout->Compra: {checkout_to_purchase:.1f}%. Revisar checkout, remarketing ou follow-up.",
                'action': 'review_checkout',
                'priority': 2
            })

    # Budget Efficiency
    if metrics['spend'] > 0 and metrics['profit'] > 0:
        margin = (metrics['profit'] / metrics['revenue']) * 100 if metrics['revenue'] > 0 else 0
        if margin >= 60:
            suggestions.append({
                'type': 'opportunity',
                'icon': '📈',
                'title': 'Margem Saudavel',
                'message': f"Margem: {margin:.0f}%. Ha espaco para aumentar budget agressivamente.",
                'action': 'aggressive_scale',
                'priority': 2
            })

    # Sort by priority
    suggestions.sort(key=lambda x: x['priority'])

    return suggestions

# =============================================================================
# SIDEBAR - CONTROLS
# =============================================================================

with st.sidebar:
    st.markdown("## 🎯 Command Center")
    st.markdown("---")

    # Period selector
    date_preset = st.selectbox(
        "Periodo de Analise",
        options=['yesterday', 'last_3d', 'last_7d', 'last_14d', 'last_30d'],
        index=1,
        format_func=lambda x: {
            'yesterday': 'Ontem',
            'last_3d': 'Ultimos 3 dias',
            'last_7d': 'Ultimos 7 dias',
            'last_14d': 'Ultimos 14 dias',
            'last_30d': 'Ultimos 30 dias'
        }.get(x, x)
    )

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Acoes Rapidas")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("📊 Exportar", use_container_width=True):
            st.info("Export em desenvolvimento")

    st.markdown("---")

    # Account Info
    st.markdown("### 📋 Conta")
    st.code(META_AD_ACCOUNT_ID, language=None)

    st.markdown("---")
    st.caption(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.markdown("# 🎯 Media Buying Command Center")
st.markdown("*Central de controle para gestao de trafego pago*")

# Fetch data
with st.spinner("Carregando dados..."):
    raw_data = fetch_account_insights(date_preset)
    metrics = parse_metrics(raw_data)
    campaigns = fetch_campaigns()

if metrics:
    # =========================================================================
    # KPI OVERVIEW
    # =========================================================================

    st.markdown("---")

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        roas_delta = "🟢 Bom" if metrics['roas'] >= 2 else ("🟡 Atencao" if metrics['roas'] >= 1.5 else "🔴 Critico")
        st.metric("ROAS", f"{metrics['roas']:.2f}x", roas_delta)
    with k2:
        st.metric("Revenue", f"${metrics['revenue']:,.0f}", f"${metrics['profit']:,.0f} profit")
    with k3:
        st.metric("Ad Spend", f"${metrics['spend']:,.0f}")
    with k4:
        cpp_delta = "🟢 Bom" if metrics['cpp'] <= 15 else ("🟡 Atencao" if metrics['cpp'] <= 20 else "🔴 Alto")
        st.metric("CPP", f"${metrics['cpp']:.2f}", cpp_delta)
    with k5:
        st.metric("Purchases", f"{int(metrics['purchases'])}")
    with k6:
        freq_delta = "🟢 OK" if metrics['frequency'] <= 2 else ("🟡 Watch" if metrics['frequency'] <= 2.5 else "🔴 Alto")
        st.metric("Frequency", f"{metrics['frequency']:.2f}", freq_delta)

    # =========================================================================
    # TABS
    # =========================================================================

    st.markdown("---")

    tab_ai, tab_campaigns, tab_adsets, tab_analytics = st.tabs([
        "🤖 Sugestoes IA",
        "📢 Campanhas",
        "🎯 Ad Sets",
        "📊 Analytics"
    ])

    # -------------------------------------------------------------------------
    # TAB: AI SUGGESTIONS
    # -------------------------------------------------------------------------

    with tab_ai:
        st.markdown("## 🤖 Sugestoes de Otimizacao")
        st.markdown("*Analise automatica baseada nos dados atuais*")

        suggestions = generate_ai_suggestions(metrics, campaigns)

        if suggestions:
            for sug in suggestions:
                css_class = f"ai-suggestion ai-suggestion-{sug['type']}" if sug['type'] in ['critical', 'opportunity'] else "ai-suggestion"
                st.markdown(f"""
                <div class="{css_class}">
                    <h3 style="margin:0 0 0.5rem 0;">{sug['icon']} {sug['title']}</h3>
                    <p style="margin:0; opacity:0.9;">{sug['message']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Todas as metricas estao dentro dos parametros saudaveis!")

        # Quick optimization summary
        st.markdown("### 📋 Resumo de Acoes")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Acoes Imediatas:**
            - Pausar ad sets com CPP > $25
            - Revisar criativos com CTR < 1%
            - Expandir publico se frequency > 2.5
            """)

        with col2:
            st.markdown(f"""
            **Oportunidades:**
            - Escalar budget se ROAS > 2.5x
            - Duplicar ads com CTR > 3%
            - Testar novos publicos lookalike
            """)

    # -------------------------------------------------------------------------
    # TAB: CAMPAIGNS
    # -------------------------------------------------------------------------

    with tab_campaigns:
        st.markdown("## 📢 Gerenciar Campanhas")

        if campaigns:
            for campaign in campaigns:
                c_id = campaign.get('id', '')
                c_name = campaign.get('name', 'Unknown')
                c_status = campaign.get('effective_status', 'UNKNOWN')
                c_budget = int(campaign.get('daily_budget', 0)) / 100 if campaign.get('daily_budget') else 0

                # Get campaign metrics
                c_insights = campaign.get('insights', {}).get('data', [{}])[0] if campaign.get('insights') else {}
                c_spend = float(c_insights.get('spend', 0))
                c_roas = float(c_insights.get('purchase_roas', [{}])[0].get('value', 0)) if c_insights.get('purchase_roas') else 0

                # Status color
                status_color = "#10B981" if c_status == "ACTIVE" else ("#F59E0B" if c_status == "PAUSED" else "#EF4444")
                status_icon = "🟢" if c_status == "ACTIVE" else ("🟡" if c_status == "PAUSED" else "🔴")

                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])

                    with col1:
                        st.markdown(f"**{c_name}**")
                        st.caption(f"ID: {c_id}")

                    with col2:
                        st.markdown(f"{status_icon} {c_status}")

                    with col3:
                        st.markdown(f"${c_spend:,.0f}")
                        st.caption("Spend")

                    with col4:
                        st.markdown(f"{c_roas:.2f}x")
                        st.caption("ROAS")

                    with col5:
                        btn_col1, btn_col2, btn_col3 = st.columns(3)

                        with btn_col1:
                            if c_status == "ACTIVE":
                                if st.button("⏸️", key=f"pause_{c_id}", help="Pausar"):
                                    result = update_campaign_status(c_id, "PAUSED")
                                    if 'error' not in result:
                                        st.success("Pausado!")
                                        st.cache_data.clear()
                                        st.rerun()
                            else:
                                if st.button("▶️", key=f"activate_{c_id}", help="Ativar"):
                                    result = update_campaign_status(c_id, "ACTIVE")
                                    if 'error' not in result:
                                        st.success("Ativado!")
                                        st.cache_data.clear()
                                        st.rerun()

                        with btn_col2:
                            if st.button("📈", key=f"up_{c_id}", help="+20% Budget"):
                                if c_budget > 0:
                                    new_budget = int(c_budget * 1.2 * 100)
                                    result = update_budget(c_id, new_budget)
                                    if 'error' not in result:
                                        st.success(f"Budget: ${new_budget/100:.0f}")
                                        st.cache_data.clear()

                        with btn_col3:
                            if st.button("📉", key=f"down_{c_id}", help="-20% Budget"):
                                if c_budget > 0:
                                    new_budget = int(c_budget * 0.8 * 100)
                                    result = update_budget(c_id, new_budget)
                                    if 'error' not in result:
                                        st.success(f"Budget: ${new_budget/100:.0f}")
                                        st.cache_data.clear()

                    st.markdown("---")
        else:
            st.info("Nenhuma campanha encontrada.")

        # Bulk Actions
        st.markdown("### ⚡ Acoes em Massa")

        bulk_col1, bulk_col2, bulk_col3, bulk_col4 = st.columns(4)

        with bulk_col1:
            if st.button("⏸️ Pausar Todas", use_container_width=True):
                for c in campaigns:
                    if c.get('effective_status') == 'ACTIVE':
                        update_campaign_status(c['id'], 'PAUSED')
                st.cache_data.clear()
                st.rerun()

        with bulk_col2:
            if st.button("▶️ Ativar Todas", use_container_width=True):
                for c in campaigns:
                    if c.get('effective_status') == 'PAUSED':
                        update_campaign_status(c['id'], 'ACTIVE')
                st.cache_data.clear()
                st.rerun()

        with bulk_col3:
            if st.button("📈 +20% Budget Geral", use_container_width=True):
                for c in campaigns:
                    budget = int(c.get('daily_budget', 0))
                    if budget > 0:
                        update_budget(c['id'], int(budget * 1.2))
                st.cache_data.clear()
                st.rerun()

        with bulk_col4:
            if st.button("📉 -20% Budget Geral", use_container_width=True):
                for c in campaigns:
                    budget = int(c.get('daily_budget', 0))
                    if budget > 0:
                        update_budget(c['id'], int(budget * 0.8))
                st.cache_data.clear()
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB: AD SETS
    # -------------------------------------------------------------------------

    with tab_adsets:
        st.markdown("## 🎯 Gerenciar Ad Sets")

        adsets = fetch_adsets()

        if adsets:
            # Sort by spend (highest first)
            adsets_sorted = sorted(adsets, key=lambda x: float(x.get('insights', {}).get('data', [{}])[0].get('spend', 0)) if x.get('insights') else 0, reverse=True)

            for adset in adsets_sorted[:20]:  # Show top 20
                a_id = adset.get('id', '')
                a_name = adset.get('name', 'Unknown')
                a_status = adset.get('effective_status', 'UNKNOWN')
                a_budget = int(adset.get('daily_budget', 0)) / 100 if adset.get('daily_budget') else 0

                a_insights = adset.get('insights', {}).get('data', [{}])[0] if adset.get('insights') else {}
                a_spend = float(a_insights.get('spend', 0))
                a_ctr = float(a_insights.get('ctr', 0))
                a_cpc = float(a_insights.get('cpc', 0))

                status_icon = "🟢" if a_status == "ACTIVE" else ("🟡" if a_status == "PAUSED" else "🔴")

                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])

                    with col1:
                        st.markdown(f"**{a_name[:40]}...**" if len(a_name) > 40 else f"**{a_name}**")

                    with col2:
                        st.markdown(f"{status_icon}")

                    with col3:
                        st.markdown(f"${a_spend:,.0f}")

                    with col4:
                        st.markdown(f"{a_ctr:.2f}%")

                    with col5:
                        st.markdown(f"${a_cpc:.2f}")

                    with col6:
                        if a_status == "ACTIVE":
                            if st.button("⏸️", key=f"pause_as_{a_id}"):
                                update_adset_status(a_id, "PAUSED")
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            if st.button("▶️", key=f"activate_as_{a_id}"):
                                update_adset_status(a_id, "ACTIVE")
                                st.cache_data.clear()
                                st.rerun()

                st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        else:
            st.info("Nenhum ad set encontrado.")

    # -------------------------------------------------------------------------
    # TAB: ANALYTICS
    # -------------------------------------------------------------------------

    with tab_analytics:
        st.markdown("## 📊 Analytics Detalhado")

        # Funnel Chart
        st.markdown("### 🔄 Funil de Conversao")

        funnel_data = {
            'Stage': ['Impressions', 'Clicks', 'LP Views', 'Checkouts', 'Purchases'],
            'Value': [
                metrics['impressions'],
                metrics['clicks'],
                int(metrics['lp_views']),
                int(metrics['checkouts']),
                int(metrics['purchases'])
            ]
        }

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data['Stage'],
            x=funnel_data['Value'],
            textposition="auto",
            texttemplate="%{value:,}",
            marker=dict(color=['#6366F1', '#8B5CF6', '#A78BFA', '#C4B5FD', '#10B981'])
        ))

        fig_funnel.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

        # Conversion Rates
        st.markdown("### 📈 Taxas de Conversao")

        r1, r2, r3, r4 = st.columns(4)

        ctr = metrics['ctr']
        lp_rate = (metrics['lp_views'] / metrics['clicks'] * 100) if metrics['clicks'] > 0 else 0
        checkout_rate = (metrics['checkouts'] / metrics['lp_views'] * 100) if metrics['lp_views'] > 0 else 0
        close_rate = (metrics['purchases'] / metrics['checkouts'] * 100) if metrics['checkouts'] > 0 else 0

        with r1:
            st.metric("CTR", f"{ctr:.2f}%", "Target: >2%")
        with r2:
            st.metric("Click→LP", f"{lp_rate:.1f}%", "Target: >40%")
        with r3:
            st.metric("LP→Checkout", f"{checkout_rate:.1f}%", "Target: >5%")
        with r4:
            st.metric("Checkout→Purchase", f"{close_rate:.1f}%", "Target: >50%")

        # Revenue Breakdown
        st.markdown("### 💰 Breakdown Financeiro")

        fig_pie = go.Figure(data=[go.Pie(
            labels=['Ad Spend', 'Profit'],
            values=[metrics['spend'], metrics['profit']],
            hole=0.6,
            marker_colors=['#EF4444', '#10B981']
        )])

        fig_pie.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(orientation='h', y=-0.1),
            annotations=[dict(text=f'${metrics["revenue"]:,.0f}', x=0.5, y=0.5, font_size=20, showarrow=False, font_color='white')]
        )

        st.plotly_chart(fig_pie, use_container_width=True)

        # Commission Summary
        st.markdown("### 💼 Comissao da Agencia")

        commission = metrics['profit'] * 0.20
        days_map = {'yesterday': 1, 'last_3d': 3, 'last_7d': 7, 'last_14d': 14, 'last_30d': 30}
        days = days_map.get(date_preset, 3)
        daily_commission = commission / days

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Profit do Periodo", f"${metrics['profit']:,.2f}")
        with c2:
            st.metric("Comissao (20%)", f"${commission:,.2f}")
        with c3:
            st.metric("Projecao Semanal", f"${daily_commission * 7:,.2f}")
        with c4:
            st.metric("Projecao Mensal", f"${daily_commission * 30:,.2f}")

else:
    st.error("❌ Erro ao carregar dados da API do Meta")
    st.info("Verifique se META_ACCESS_TOKEN e META_AD_ACCOUNT_ID estao configurados corretamente.")

    with st.expander("Debug Info"):
        st.code(f"Account ID: {META_AD_ACCOUNT_ID}")
        st.code(f"Token: {META_ACCESS_TOKEN[:20]}..." if META_ACCESS_TOKEN else "Token: Not set")

# Footer
st.markdown("---")
st.caption(f"Media Buying Command Center · {datetime.now().strftime('%Y-%m-%d %H:%M')} · Account: {META_AD_ACCOUNT_ID}")
