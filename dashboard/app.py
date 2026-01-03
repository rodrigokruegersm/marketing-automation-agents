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
from core.adapters.google_analytics import GoogleAnalyticsAdapter, get_mock_ga_data
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
if 'ai_chat_history' not in st.session_state:
    st.session_state.ai_chat_history = []
if 'ai_chat_input' not in st.session_state:
    st.session_state.ai_chat_input = ''

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
            'hyros_key': st.secrets.get("HYROS_API_KEY", ""),
            'ga_property_id': st.secrets.get("GA_PROPERTY_ID", ""),
            'ga_credentials_json': st.secrets.get("GA_CREDENTIALS_JSON", ""),
            'openai_key': st.secrets.get("OPENAI_API_KEY", "")
        }
    except:
        return {
            'meta_token': os.getenv("META_ACCESS_TOKEN", ""),
            'meta_account': os.getenv("META_AD_ACCOUNT_ID", ""),
            'whop_key': os.getenv("WHOP_API_KEY", ""),
            'hyros_key': os.getenv("HYROS_API_KEY", ""),
            'ga_property_id': os.getenv("GA_PROPERTY_ID", ""),
            'ga_credentials_json': os.getenv("GA_CREDENTIALS_JSON", ""),
            'openai_key': os.getenv("OPENAI_API_KEY", "")
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
# GOOGLE ANALYTICS DATA
# =============================================================================

@st.cache_data(ttl=120)
def fetch_ga_data(property_id: str, credentials_json: str, start_date: str, end_date: str):
    """Fetch Google Analytics data for the specified date range"""
    if not property_id:
        # Return mock data for demo purposes
        return get_mock_ga_data()

    try:
        ga_adapter = GoogleAnalyticsAdapter(
            property_id=property_id,
            credentials_json=credentials_json
        )
        return ga_adapter.get_full_report(start_date, end_date)
    except Exception as e:
        # Return mock data if GA connection fails
        return get_mock_ga_data()

def calculate_delta(current: float, previous: float) -> dict:
    """Calculate delta between two values with trend indicator"""
    if previous == 0:
        if current > 0:
            return {'delta': 100.0, 'trend': 'up', 'icon': '↑'}
        return {'delta': 0, 'trend': 'flat', 'icon': '→'}

    delta_pct = ((current - previous) / abs(previous)) * 100

    if delta_pct > 5:
        return {'delta': delta_pct, 'trend': 'up', 'icon': '↑'}
    elif delta_pct < -5:
        return {'delta': delta_pct, 'trend': 'down', 'icon': '↓'}
    else:
        return {'delta': delta_pct, 'trend': 'flat', 'icon': '→'}

def get_delta_color(trend: str, metric_type: str = 'positive') -> str:
    """Get color for delta based on trend and metric type"""
    # For metrics where higher is better (revenue, ROAS, etc.)
    if metric_type == 'positive':
        if trend == 'up':
            return '#10B981'  # green
        elif trend == 'down':
            return '#EF4444'  # red
    # For metrics where lower is better (CPA, CPM, etc.)
    elif metric_type == 'negative':
        if trend == 'up':
            return '#EF4444'  # red
        elif trend == 'down':
            return '#10B981'  # green
    return '#94A3B8'  # gray for flat

def cross_reference_data(meta_metrics: dict, ga_data: dict) -> dict:
    """Cross-reference Meta Ads data with Google Analytics"""
    meta_purchases = meta_metrics.get('purchases', 0)
    meta_revenue = meta_metrics.get('revenue', 0)
    meta_spend = meta_metrics.get('spend', 0)

    # GA data
    ga_overview = ga_data.get('overview', {})
    ga_sessions = ga_overview.get('sessions', 0)
    ga_users = ga_overview.get('users', 0)
    ga_transactions = ga_overview.get('transactions', 0)
    ga_revenue = ga_overview.get('revenue', 0)
    ga_bounce_rate = ga_overview.get('bounce_rate', 0)
    ga_avg_session_duration = ga_overview.get('avg_session_duration', 0)

    # Calculate cross-platform insights
    meta_lp_views = meta_metrics.get('landing_page_views', 0)

    # Session to LP View ratio (data quality check)
    session_lp_ratio = (ga_sessions / meta_lp_views * 100) if meta_lp_views > 0 else 0

    # Attribution comparison
    purchase_diff = meta_purchases - ga_transactions
    revenue_diff = meta_revenue - ga_revenue

    # True cost metrics
    true_roas = ga_revenue / meta_spend if meta_spend > 0 else 0
    true_cpa = meta_spend / ga_transactions if ga_transactions > 0 else 0

    return {
        # Meta Ads data
        'meta_purchases': meta_purchases,
        'meta_revenue': meta_revenue,
        'meta_spend': meta_spend,
        'meta_roas': meta_metrics.get('roas', 0),
        'meta_lp_views': meta_lp_views,

        # GA data
        'ga_sessions': ga_sessions,
        'ga_users': ga_users,
        'ga_transactions': ga_transactions,
        'ga_revenue': ga_revenue,
        'ga_bounce_rate': ga_bounce_rate,
        'ga_avg_session_duration': ga_avg_session_duration,

        # Cross-platform insights
        'session_lp_ratio': session_lp_ratio,
        'purchase_diff': purchase_diff,
        'revenue_diff': revenue_diff,
        'true_roas': true_roas,
        'true_cpa': true_cpa,

        # Traffic sources from GA
        'traffic_sources': ga_data.get('traffic_sources', {}),
        'channels': ga_data.get('channels', {}),
        'devices': ga_data.get('devices', {}),
        'top_pages': ga_data.get('top_pages', []),
        'landing_pages': ga_data.get('landing_pages', [])
    }

def generate_improvement_suggestions(metrics_3d: dict, metrics_7d: dict, cross_data: dict) -> list:
    """Generate actionable improvement suggestions based on all data"""
    suggestions = []

    # ROAS improvements
    roas_7d = metrics_7d.get('roas', 0)
    if roas_7d < 2.0:
        suggestions.append({
            'priority': 'high',
            'category': 'ROAS',
            'icon': '💰',
            'title': 'Aumentar ROAS',
            'current': f'{roas_7d:.2f}x',
            'target': '2.0x+',
            'actions': [
                'Pausar adsets com ROAS < 1.0x',
                'Duplicar criativos vencedores',
                'Testar audiences mais qualificadas',
                'Revisar página de vendas (copy, oferta, garantia)'
            ]
        })

    # CTR improvements
    ctr_7d = metrics_7d.get('ctr', 0)
    if ctr_7d < 1.0:
        suggestions.append({
            'priority': 'medium',
            'category': 'CTR',
            'icon': '🖱️',
            'title': 'Melhorar Click-Through Rate',
            'current': f'{ctr_7d:.2f}%',
            'target': '1.5%+',
            'actions': [
                'Testar novos hooks nos primeiros 3 segundos',
                'Usar mais pattern interrupts nos criativos',
                'Atualizar copies com urgência/escassez',
                'Testar thumbnails mais chamativas'
            ]
        })

    # LP View Rate improvements
    lp_rate = metrics_7d.get('lp_view_rate', 0)
    if lp_rate < 70:
        suggestions.append({
            'priority': 'medium',
            'category': 'LP View Rate',
            'icon': '📄',
            'title': 'Aumentar Taxa de Visualização LP',
            'current': f'{lp_rate:.1f}%',
            'target': '80%+',
            'actions': [
                'Otimizar velocidade da landing page',
                'Verificar mobile responsiveness',
                'Reduzir tempo de carregamento < 3s',
                'Usar CDN para assets estáticos'
            ]
        })

    # Checkout rate improvements
    checkouts = metrics_7d.get('initiate_checkout', 0)
    purchases = metrics_7d.get('purchases', 0)
    checkout_rate = (purchases / checkouts * 100) if checkouts > 0 else 0
    if checkout_rate < 30:
        suggestions.append({
            'priority': 'high',
            'category': 'Checkout',
            'icon': '🛒',
            'title': 'Melhorar Conversão de Checkout',
            'current': f'{checkout_rate:.1f}%',
            'target': '40%+',
            'actions': [
                'Simplificar formulário de checkout',
                'Adicionar mais métodos de pagamento (Pix, boleto)',
                'Mostrar garantia e políticas de devolução',
                'Adicionar prova social no checkout',
                'Implementar exit intent popup'
            ]
        })

    # Frequency issues
    freq_7d = metrics_7d.get('frequency', 0)
    if freq_7d > 2.5:
        suggestions.append({
            'priority': 'high' if freq_7d > 3.5 else 'medium',
            'category': 'Frequência',
            'icon': '🔄',
            'title': 'Reduzir Frequência de Anúncio',
            'current': f'{freq_7d:.1f}x',
            'target': '< 2.5x',
            'actions': [
                'Expandir tamanho da audiência',
                'Criar novos lookalikes 1-3%',
                'Adicionar interesses relacionados',
                'Rodar mais criativos variados',
                'Pausar adsets com freq > 4x'
            ]
        })

    # GA Bounce Rate
    bounce_rate = cross_data.get('ga_bounce_rate', 0)
    if bounce_rate > 60:
        suggestions.append({
            'priority': 'medium',
            'category': 'Bounce Rate',
            'icon': '📉',
            'title': 'Reduzir Taxa de Rejeição',
            'current': f'{bounce_rate:.1f}%',
            'target': '< 50%',
            'actions': [
                'Melhorar alinhamento anúncio ↔ landing page',
                'Adicionar conteúdo above the fold',
                'Melhorar proposta de valor no hero',
                'Adicionar vídeo explicativo'
            ]
        })

    # Attribution gap
    purchase_diff = cross_data.get('purchase_diff', 0)
    if abs(purchase_diff) > 5:
        suggestions.append({
            'priority': 'low',
            'category': 'Atribuição',
            'icon': '📊',
            'title': 'Verificar Atribuição',
            'current': f'{purchase_diff:+d} vendas diff',
            'target': 'Alinhar Meta ↔ GA',
            'actions': [
                'Verificar configuração do Pixel',
                'Checar eventos duplicados',
                'Revisar janela de atribuição',
                'Considerar usar Hyros para atribuição'
            ]
        })

    return sorted(suggestions, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])

def generate_ai_response(question: str, metrics_3d: dict, metrics_7d: dict, cross_data: dict, suggestions: list) -> str:
    """Generate AI response based on the question and available data"""
    # Build context from all data
    context = f"""
DADOS DOS ÚLTIMOS 3 DIAS:
- ROAS: {metrics_3d.get('roas', 0):.2f}x
- Gasto: ${metrics_3d.get('spend', 0):,.2f}
- Faturamento: ${metrics_3d.get('revenue', 0):,.2f}
- Vendas: {metrics_3d.get('purchases', 0)}
- CTR: {metrics_3d.get('ctr', 0):.2f}%
- Frequência: {metrics_3d.get('frequency', 0):.2f}

DADOS DOS ÚLTIMOS 7 DIAS:
- ROAS: {metrics_7d.get('roas', 0):.2f}x
- Gasto: ${metrics_7d.get('spend', 0):,.2f}
- Faturamento: ${metrics_7d.get('revenue', 0):,.2f}
- Vendas: {metrics_7d.get('purchases', 0)}
- CTR: {metrics_7d.get('ctr', 0):.2f}%
- CPA: ${metrics_7d.get('cpa', 0):,.2f}
- Frequência: {metrics_7d.get('frequency', 0):.2f}
- Hook Rate: {metrics_7d.get('hook_rate', 0):.2f}%
- LP View Rate: {metrics_7d.get('lp_view_rate', 0):.1f}%

DADOS GOOGLE ANALYTICS:
- Sessões: {cross_data.get('ga_sessions', 0):,}
- Usuários: {cross_data.get('ga_users', 0):,}
- Transações GA: {cross_data.get('ga_transactions', 0)}
- Bounce Rate: {cross_data.get('ga_bounce_rate', 0):.1f}%
- True ROAS (GA): {cross_data.get('true_roas', 0):.2f}x

MELHORIAS PRIORITÁRIAS:
{chr(10).join([f"- {s['title']} ({s['current']} → {s['target']})" for s in suggestions[:3]])}
"""

    # Simple rule-based responses (can be replaced with OpenAI API)
    question_lower = question.lower()

    if 'roas' in question_lower or 'retorno' in question_lower:
        roas_7d = metrics_7d.get('roas', 0)
        roas_3d = metrics_3d.get('roas', 0)
        trend = "subindo" if roas_3d > roas_7d else "caindo" if roas_3d < roas_7d else "estável"

        if roas_7d < 1.0:
            return f"""📊 **Análise de ROAS:**

O ROAS atual de **{roas_7d:.2f}x** está abaixo do breakeven. Nos últimos 3 dias está {trend} ({roas_3d:.2f}x).

**Ação Urgente Necessária:**
1. Pausar todos os adsets com ROAS < 0.8x imediatamente
2. Revisar os criativos que estão rodando
3. Verificar se a página de vendas está convertendo
4. Considerar pausar as campanhas por 24h para reset do algoritmo

**Meta:** Atingir ROAS > 2.0x para ter margem saudável."""

        elif roas_7d < 2.0:
            return f"""📊 **Análise de ROAS:**

O ROAS de **{roas_7d:.2f}x** está na zona de atenção. Tendência: {trend} ({roas_3d:.2f}x em 3d).

**Recomendações:**
1. Manter budget atual, não escalar ainda
2. Analisar quais adsets têm ROAS > 2x e duplicá-los
3. Pausar adsets com ROAS consistentemente < 1.5x
4. Testar 2-3 novos criativos por semana
5. Revisar copy e CTA da landing page

**Meta:** Estabilizar em 2.0x+ antes de escalar."""

        else:
            return f"""📊 **Análise de ROAS:**

Excelente! ROAS de **{roas_7d:.2f}x** está saudável. Tendência: {trend} ({roas_3d:.2f}x em 3d).

**Oportunidades de Scale:**
1. Aumentar budget 20-30% nos adsets vencedores
2. Duplicar winners para novas audiências
3. Testar lookalikes 1-3% dos compradores
4. Manter os criativos atuais rodando

**Atenção:** Monitorar frequência - se passar de 2.5x, expandir audiência."""

    elif 'escalar' in question_lower or 'scale' in question_lower:
        roas_7d = metrics_7d.get('roas', 0)
        freq_7d = metrics_7d.get('frequency', 0)

        if roas_7d >= 2.0 and freq_7d < 2.5:
            return f"""🚀 **Análise de Scale:**

**Você está pronto para escalar!**
- ROAS: {roas_7d:.2f}x ✅
- Frequência: {freq_7d:.1f}x ✅

**Estratégia de Scale Recomendada:**
1. **Dia 1-3:** Aumente budget em 20% nos top 3 adsets
2. **Dia 4-7:** Se ROAS mantiver > 2x, aumente mais 20%
3. **Dia 8+:** Duplique os winners para novas audiências

**Regras de Ouro:**
- Nunca aumente mais de 30% por vez
- Aguarde 48h entre aumentos para o algoritmo estabilizar
- Monitore CPA e frequência diariamente"""

        elif roas_7d >= 2.0 and freq_7d >= 2.5:
            return f"""⚠️ **Análise de Scale:**

ROAS bom ({roas_7d:.2f}x), mas **frequência alta** ({freq_7d:.1f}x).

**Antes de escalar:**
1. Expandir audiência em 50%+ para reduzir frequência
2. Adicionar 3-5 novos interesses relacionados
3. Criar lookalikes de compradores (1%, 2%, 3%)
4. Preparar 3-5 novos criativos para rotação

**Escale apenas após** frequência voltar para < 2.5x."""

        else:
            return f"""⏸️ **Análise de Scale:**

**Ainda não é hora de escalar.**
- ROAS atual: {roas_7d:.2f}x (meta: > 2.0x)
- Frequência: {freq_7d:.1f}x

**Foque em otimização primeiro:**
1. Pausar adsets com ROAS < 1.5x
2. Testar novos ângulos de criativos
3. Otimizar landing page para conversão
4. Alcançar ROAS consistente > 2.0x por 5+ dias"""

    elif 'criativo' in question_lower or 'creative' in question_lower:
        hook_rate = metrics_7d.get('hook_rate', 0)
        ctr = metrics_7d.get('ctr', 0)

        return f"""🎨 **Análise de Criativos:**

**Métricas Atuais:**
- Hook Rate: {hook_rate:.2f}% {'✅' if hook_rate > 25 else '⚠️' if hook_rate > 15 else '❌'}
- CTR: {ctr:.2f}% {'✅' if ctr > 1.5 else '⚠️' if ctr > 0.8 else '❌'}

**{'Seus criativos estão funcionando bem!' if hook_rate > 25 and ctr > 1.5 else 'Oportunidades de melhoria:'}**

{'Mantenha os winners e teste variações.' if hook_rate > 25 else '''1. **Hook fraco** - teste novos primeiros 3 segundos:
   - Pergunta provocativa
   - Número/estatística impactante
   - Promessa direta do benefício
   - Pattern interrupt visual'''}

{'Continue monitorando CTR.' if ctr > 1.5 else '''2. **CTR baixo** - melhore o call-to-action:
   - CTA mais claro e urgente
   - Benefício principal no texto
   - Prova social no criativo'''}

**Regra dos 3x3:**
Teste 3 hooks diferentes + 3 bodies diferentes = 9 combinações."""

    elif 'audiencia' in question_lower or 'publico' in question_lower or 'audience' in question_lower:
        freq = metrics_7d.get('frequency', 0)

        return f"""👥 **Análise de Audiência:**

**Frequência Atual:** {freq:.1f}x {'✅' if freq < 2.5 else '⚠️' if freq < 3.5 else '❌'}

{'Audiência saudável - frequência controlada.' if freq < 2.5 else f'''**Audiência Saturada!** Frequência de {freq:.1f}x indica que as mesmas pessoas estão vendo os anúncios repetidamente.

**Ações Imediatas:**
1. Expandir público em 50-100%
2. Adicionar novos interesses relacionados
3. Testar lookalikes 1-5% de:
   - Compradores
   - Add to carts
   - View content (site)
4. Excluir quem já comprou nos últimos 180 dias'''}

**Estrutura de Audiências Recomendada:**
- 🎯 **Hot:** Retargeting 7 dias (30% budget)
- 🔥 **Warm:** Retargeting 30 dias + Lookalike 1% (40% budget)
- ❄️ **Cold:** Lookalikes 2-5% + Interesses (30% budget)"""

    else:
        # Generic response with summary
        return f"""📋 **Resumo Geral do Traffic:**

**Performance (7 dias):**
- ROAS: {metrics_7d.get('roas', 0):.2f}x
- Gasto: ${metrics_7d.get('spend', 0):,.2f}
- Faturamento: ${metrics_7d.get('revenue', 0):,.2f}
- Vendas: {metrics_7d.get('purchases', 0)}
- CPA: ${metrics_7d.get('cpa', 0):,.2f}

**Saúde do Funil:**
- CTR: {metrics_7d.get('ctr', 0):.2f}%
- Hook Rate: {metrics_7d.get('hook_rate', 0):.2f}%
- LP View Rate: {metrics_7d.get('lp_view_rate', 0):.1f}%
- Frequência: {metrics_7d.get('frequency', 0):.1f}x

**Próximos Passos:**
{chr(10).join([f"• {s['title']}" for s in suggestions[:3]])}

💡 *Pergunte sobre ROAS, escalar, criativos ou audiências para análises específicas.*"""

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
    st.markdown(f"{'🟢' if creds['ga_property_id'] else '🟡'} Google Analytics")
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
    st.markdown("*Análise avançada com cruzamento Meta Ads + Google Analytics*")

    if creds['meta_token'] and creds['meta_account']:

        # ========== DATE FILTER (Meta Ads Manager Style) ==========
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

        # Fetch data for selected period AND comparison periods (3d, 7d)
        if use_custom_dates:
            insights = fetch_account_insights(creds['meta_account'], creds['meta_token'], start_date=start_date_str, end_date=end_date_str)
            campaigns = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], start_date=start_date_str, end_date=end_date_str)
        else:
            insights = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)
            campaigns = fetch_campaigns_with_insights(creds['meta_account'], creds['meta_token'], date_preset=date_preset)

        # Always fetch 3d and 7d for comparison
        insights_3d = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset='last_3d')
        insights_7d = fetch_account_insights(creds['meta_account'], creds['meta_token'], date_preset='last_7d')

        metrics = parse_full_metrics(insights)
        metrics_3d = parse_full_metrics(insights_3d)
        metrics_7d = parse_full_metrics(insights_7d)

        # Fetch GA data for both 3d and 7d
        ga_start_7d = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        ga_start_3d = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
        ga_end = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        ga_data_7d = fetch_ga_data(creds['ga_property_id'], creds['ga_credentials_json'], ga_start_7d, ga_end)
        ga_data_3d = fetch_ga_data(creds['ga_property_id'], creds['ga_credentials_json'], ga_start_3d, ga_end)
        ga_data = ga_data_7d  # Maintain backwards compatibility

        # Cross-reference data
        cross_data = cross_reference_data(metrics_7d, ga_data_7d)
        cross_data_3d = cross_reference_data(metrics_3d, ga_data_3d)

        # Generate improvement suggestions
        suggestions = generate_improvement_suggestions(metrics_3d, metrics_7d, cross_data)

        # Tabs - Expanded with new sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview",
            "📈 3d vs 7d",
            "🔗 Cross-Platform",
            "💡 Melhorias",
            "📢 Campanhas",
            "🤖 AI Consultant"
        ])

        # ========== TAB 1: OVERVIEW ==========
        with tab1:
            st.markdown("### 📊 Performance Overview")

            # Top KPI Row with main metrics
            kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

            roas_class = "green" if metrics_7d['roas'] >= 2 else "yellow" if metrics_7d['roas'] >= 1 else "red"
            profit_class = "green" if metrics_7d['profit'] > 0 else "red"

            with kpi_col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Faturamento (7d)</div>
                    <div class="kpi-value green">${metrics_7d['revenue']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Gasto (7d)</div>
                    <div class="kpi-value">${metrics_7d['spend']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">ROAS (7d)</div>
                    <div class="kpi-value {roas_class}">{metrics_7d['roas']:.2f}x</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Lucro (7d)</div>
                    <div class="kpi-value {profit_class}">${metrics_7d['profit']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col5:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Vendas (7d)</div>
                    <div class="kpi-value">{metrics_7d['purchases']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Funnel visualization
            st.markdown("""
            <div class="funnel-container">
                <div class="funnel-title">🎯 Funil de Conversão (7 dias)</div>
            """, unsafe_allow_html=True)

            # Calculate rates
            impr = metrics_7d['impressions']
            clicks = metrics_7d['link_clicks'] if metrics_7d['link_clicks'] > 0 else metrics_7d['clicks']
            lp_views = metrics_7d['landing_page_views']
            checkouts = metrics_7d['initiate_checkout']
            purchases = metrics_7d['purchases']

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

            # Charts row
            col1, col2 = st.columns(2)

            with col1:
                # Funnel chart
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
                    title="Funil Visual",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F8FAFC'},
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # ROAS Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics_7d['roas'],
                    delta={'reference': metrics_3d['roas'], 'relative': True, 'valueformat': '.1%'},
                    number={'suffix': 'x', 'font': {'size': 40, 'color': '#F8FAFC'}},
                    title={'text': "ROAS (7d vs 3d)", 'font': {'size': 14, 'color': '#94A3B8'}},
                    gauge={
                        'axis': {'range': [0, 5], 'tickcolor': '#475569'},
                        'bar': {'color': "#0066FF"},
                        'bgcolor': "#1E293B",
                        'steps': [
                            {'range': [0, 1], 'color': "rgba(239, 68, 68, 0.3)"},
                            {'range': [1, 2], 'color': "rgba(245, 158, 11, 0.3)"},
                            {'range': [2, 5], 'color': "rgba(16, 185, 129, 0.3)"}
                        ],
                        'threshold': {
                            'line': {'color': "#10B981", 'width': 4},
                            'thickness': 0.75,
                            'value': 2.0
                        }
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F8FAFC'},
                    height=350,
                    margin=dict(t=80, b=0, l=30, r=30)
                )
                st.plotly_chart(fig, use_container_width=True)

            # Secondary metrics
            st.markdown("### 📈 Métricas Secundárias")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("CTR", f"{metrics_7d['ctr']:.2f}%")
            col2.metric("CPC", f"${metrics_7d['cpc']:.2f}")
            col3.metric("CPM", f"${metrics_7d['cpm']:.2f}")
            col4.metric("Frequência", f"{metrics_7d['frequency']:.2f}")
            col5.metric("Hook Rate", f"{metrics_7d['hook_rate']:.2f}%")
            col6.metric("CPA", f"${metrics_7d['cpa']:.2f}")

        # ========== TAB 2: 3D vs 7D COMPARISON ==========
        with tab2:
            st.markdown("### 📈 Comparação 3 dias vs 7 dias")
            st.markdown("*Identificar tendências de alta ou queda em cada métrica*")

            # Calculate all deltas
            deltas = {
                'roas': calculate_delta(metrics_3d['roas'], metrics_7d['roas']),
                'spend': calculate_delta(metrics_3d['spend'], metrics_7d['spend'] / 7 * 3),  # Normalize to 3d equivalent
                'revenue': calculate_delta(metrics_3d['revenue'], metrics_7d['revenue'] / 7 * 3),
                'purchases': calculate_delta(metrics_3d['purchases'], metrics_7d['purchases'] / 7 * 3),
                'ctr': calculate_delta(metrics_3d['ctr'], metrics_7d['ctr']),
                'cpc': calculate_delta(metrics_3d['cpc'], metrics_7d['cpc']),
                'cpm': calculate_delta(metrics_3d['cpm'], metrics_7d['cpm']),
                'frequency': calculate_delta(metrics_3d['frequency'], metrics_7d['frequency']),
                'cpa': calculate_delta(metrics_3d['cpa'], metrics_7d['cpa']),
                'hook_rate': calculate_delta(metrics_3d['hook_rate'], metrics_7d['hook_rate']),
                'lp_view_rate': calculate_delta(metrics_3d['lp_view_rate'], metrics_7d['lp_view_rate'])
            }

            # Comparison table
            st.markdown("#### 💰 Financeiro")
            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)

            with fin_col1:
                d = deltas['roas']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">ROAS</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{metrics_3d['roas']:.2f}x</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{metrics_7d['roas']:.2f}x</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with fin_col2:
                d = deltas['revenue']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Faturamento</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>${metrics_3d['revenue']:,.0f}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>${metrics_7d['revenue']:,.0f}</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with fin_col3:
                d = deltas['spend']
                color = get_delta_color(d['trend'], 'negative')  # Less spend is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Gasto</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>${metrics_3d['spend']:,.0f}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>${metrics_7d['spend']:,.0f}</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with fin_col4:
                d = deltas['cpa']
                color = get_delta_color(d['trend'], 'negative')  # Less CPA is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">CPA</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>${metrics_3d['cpa']:.2f}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>${metrics_7d['cpa']:.2f}</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 🖱️ Engajamento")
            eng_col1, eng_col2, eng_col3, eng_col4 = st.columns(4)

            with eng_col1:
                d = deltas['ctr']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">CTR</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{metrics_3d['ctr']:.2f}%</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{metrics_7d['ctr']:.2f}%</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with eng_col2:
                d = deltas['hook_rate']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Hook Rate</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{metrics_3d['hook_rate']:.2f}%</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{metrics_7d['hook_rate']:.2f}%</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with eng_col3:
                d = deltas['cpc']
                color = get_delta_color(d['trend'], 'negative')  # Less CPC is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">CPC</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>${metrics_3d['cpc']:.2f}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>${metrics_7d['cpc']:.2f}</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with eng_col4:
                d = deltas['frequency']
                color = get_delta_color(d['trend'], 'negative')  # Less frequency is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Frequência</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{metrics_3d['frequency']:.2f}x</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{metrics_7d['frequency']:.2f}x</strong></div>
                        </div>
                        <div style="font-size: 24px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Trend summary
            st.markdown("---")
            st.markdown("#### 📊 Resumo de Tendências")

            up_metrics = [k for k, v in deltas.items() if v['trend'] == 'up']
            down_metrics = [k for k, v in deltas.items() if v['trend'] == 'down']

            col1, col2 = st.columns(2)

            with col1:
                if up_metrics:
                    st.markdown(f"""
                    <div class="ai-card success">
                        <div class="ai-card-title">📈 Métricas em Alta ({len(up_metrics)})</div>
                        <div class="ai-card-body">
                            {', '.join([m.upper() for m in up_metrics])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma métrica em alta significativa")

            with col2:
                if down_metrics:
                    st.markdown(f"""
                    <div class="ai-card warning">
                        <div class="ai-card-title">📉 Métricas em Queda ({len(down_metrics)})</div>
                        <div class="ai-card-body">
                            {', '.join([m.upper() for m in down_metrics])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma métrica em queda significativa")

            # Google Analytics 3d vs 7d comparison
            st.markdown("---")
            st.markdown("#### 📊 Google Analytics - 3d vs 7d")

            ga_3d_overview = ga_data_3d.get('overview', {})
            ga_7d_overview = ga_data_7d.get('overview', {})

            # Normalize 7d to 3d equivalent for fair comparison
            ga_deltas = {
                'sessions': calculate_delta(
                    ga_3d_overview.get('sessions', 0),
                    ga_7d_overview.get('sessions', 0) / 7 * 3
                ),
                'users': calculate_delta(
                    ga_3d_overview.get('users', 0),
                    ga_7d_overview.get('users', 0) / 7 * 3
                ),
                'bounce_rate': calculate_delta(
                    ga_3d_overview.get('bounce_rate', 0),
                    ga_7d_overview.get('bounce_rate', 0)
                ),
                'avg_session_duration': calculate_delta(
                    ga_3d_overview.get('avg_session_duration', 0),
                    ga_7d_overview.get('avg_session_duration', 0)
                ),
                'conversions': calculate_delta(
                    ga_3d_overview.get('conversions', 0),
                    ga_7d_overview.get('conversions', 0) / 7 * 3
                )
            }

            ga_col1, ga_col2, ga_col3, ga_col4, ga_col5 = st.columns(5)

            with ga_col1:
                d = ga_deltas['sessions']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Sessões</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{ga_3d_overview.get('sessions', 0):,}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{ga_7d_overview.get('sessions', 0):,}</strong></div>
                        </div>
                        <div style="font-size: 20px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ga_col2:
                d = ga_deltas['users']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Usuários</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{ga_3d_overview.get('users', 0):,}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{ga_7d_overview.get('users', 0):,}</strong></div>
                        </div>
                        <div style="font-size: 20px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ga_col3:
                d = ga_deltas['bounce_rate']
                color = get_delta_color(d['trend'], 'negative')  # Less bounce is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Bounce Rate</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{ga_3d_overview.get('bounce_rate', 0):.1f}%</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{ga_7d_overview.get('bounce_rate', 0):.1f}%</strong></div>
                        </div>
                        <div style="font-size: 20px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ga_col4:
                d = ga_deltas['avg_session_duration']
                color = get_delta_color(d['trend'], 'positive')  # More time is better
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Duração Média</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{ga_3d_overview.get('avg_session_duration', 0):.0f}s</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{ga_7d_overview.get('avg_session_duration', 0):.0f}s</strong></div>
                        </div>
                        <div style="font-size: 20px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ga_col5:
                d = ga_deltas['conversions']
                color = get_delta_color(d['trend'], 'positive')
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Conversões (GA)</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: #64748B;">3d: <strong>{ga_3d_overview.get('conversions', 0)}</strong></div>
                            <div style="font-size: 12px; color: #64748B;">7d: <strong>{ga_7d_overview.get('conversions', 0)}</strong></div>
                        </div>
                        <div style="font-size: 20px; color: {color}; font-weight: bold;">
                            {d['icon']} {d['delta']:+.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # True ROAS comparison
            st.markdown("---")
            st.markdown("#### 📈 True ROAS (GA) vs Meta ROAS")

            true_roas_3d = cross_data_3d.get('true_roas', 0)
            true_roas_7d = cross_data.get('true_roas', 0)
            meta_roas_3d = metrics_3d.get('roas', 0)
            meta_roas_7d = metrics_7d.get('roas', 0)

            roas_col1, roas_col2 = st.columns(2)

            with roas_col1:
                st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #0066FF;">
                    <div class="kpi-label">Meta ROAS</div>
                    <div style="font-size: 28px; font-weight: bold; color: #F8FAFC;">
                        3d: {meta_roas_3d:.2f}x | 7d: {meta_roas_7d:.2f}x
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with roas_col2:
                true_roas_color = '#10B981' if true_roas_7d >= 1.5 else '#F59E0B' if true_roas_7d >= 1.0 else '#EF4444'
                st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #E37400;">
                    <div class="kpi-label">True ROAS (GA)</div>
                    <div style="font-size: 28px; font-weight: bold; color: {true_roas_color};">
                        3d: {true_roas_3d:.2f}x | 7d: {true_roas_7d:.2f}x
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ========== TAB 3: CROSS-PLATFORM ==========
        with tab3:
            st.markdown("### 🔗 Cruzamento Meta Ads + Google Analytics")
            st.markdown("*Dados de 7 dias - comparando atribuição entre plataformas*")

            # Side by side comparison
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class="card" style="border-left: 4px solid #0066FF;">
                    <h4>📘 Meta Ads</h4>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Vendas (Meta)", f"{cross_data['meta_purchases']}")
                st.metric("Faturamento (Meta)", f"${cross_data['meta_revenue']:,.2f}")
                st.metric("ROAS (Meta)", f"{cross_data['meta_roas']:.2f}x")
                st.metric("LP Views (Meta)", f"{cross_data['meta_lp_views']:,}")

            with col2:
                st.markdown("""
                <div class="card" style="border-left: 4px solid #E37400;">
                    <h4>📊 Google Analytics</h4>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Transações (GA)", f"{cross_data['ga_transactions']}")
                st.metric("Faturamento (GA)", f"${cross_data['ga_revenue']:,.2f}")
                st.metric("True ROAS (GA)", f"{cross_data['true_roas']:.2f}x")
                st.metric("Sessões (GA)", f"{cross_data['ga_sessions']:,}")

            st.markdown("---")

            # Attribution insights
            st.markdown("### 🔍 Insights de Atribuição")

            purchase_diff = cross_data['purchase_diff']
            revenue_diff = cross_data['revenue_diff']

            if purchase_diff > 0:
                st.markdown(f"""
                <div class="ai-card warning">
                    <div class="ai-card-title">⚠️ Meta reporta {purchase_diff} vendas a mais que GA</div>
                    <div class="ai-card-body">
                        Meta Ads pode estar atribuindo mais vendas devido à janela de atribuição mais longa ou eventos duplicados.
                        Considere usar o True ROAS (GA) para decisões mais conservadoras.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif purchase_diff < 0:
                st.markdown(f"""
                <div class="ai-card info">
                    <div class="ai-card-title">ℹ️ GA reporta {abs(purchase_diff)} vendas a mais que Meta</div>
                    <div class="ai-card-body">
                        GA está atribuindo mais vendas do que Meta. Pode haver vendas orgânicas ou de outros canais.
                        Verifique UTMs e configuração do Pixel.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-card success">
                    <div class="ai-card-title">✅ Atribuição Alinhada</div>
                    <div class="ai-card-body">
                        Meta e GA estão reportando o mesmo número de vendas. Excelente configuração de tracking!
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # GA Additional insights
            st.markdown("---")
            st.markdown("### 📈 Dados do Google Analytics")

            ga_col1, ga_col2, ga_col3, ga_col4 = st.columns(4)
            ga_col1.metric("Usuários", f"{cross_data['ga_users']:,}")
            ga_col2.metric("Sessões", f"{cross_data['ga_sessions']:,}")
            ga_col3.metric("Bounce Rate", f"{cross_data['ga_bounce_rate']:.1f}%")
            ga_col4.metric("Duração Média", f"{cross_data['ga_avg_session_duration']:.0f}s")

            # Channel breakdown (pie chart)
            st.markdown("#### 📊 Canais de Tráfego")
            channels = cross_data.get('channels', {})
            if channels:
                channels_df = pd.DataFrame([
                    {'Canal': k, 'Sessões': v}
                    for k, v in channels.items()
                ])
                if not channels_df.empty:
                    col_ch1, col_ch2 = st.columns([2, 1])
                    with col_ch1:
                        fig = px.pie(channels_df, values='Sessões', names='Canal', hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Set2)
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={'color': '#F8FAFC'},
                            height=300,
                            margin=dict(t=20, b=20, l=20, r=20),
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    with col_ch2:
                        total_sessions = sum(channels.values())
                        for ch, sess in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:6]:
                            pct = (sess / total_sessions * 100) if total_sessions > 0 else 0
                            st.markdown(f"**{ch}**: {sess:,} ({pct:.1f}%)")

            # Traffic sources table
            traffic_sources = cross_data.get('traffic_sources', [])
            if traffic_sources:
                st.markdown("#### 📡 Fontes de Tráfego (Source/Medium)")
                sources_df = pd.DataFrame(traffic_sources)
                if not sources_df.empty and 'source' in sources_df.columns:
                    sources_df['Source/Medium'] = sources_df['source'] + ' / ' + sources_df['medium']
                    st.dataframe(
                        sources_df[['Source/Medium', 'sessions', 'users', 'conversions']].head(10),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'Source/Medium': 'Fonte / Meio',
                            'sessions': st.column_config.NumberColumn('Sessões', format='%d'),
                            'users': st.column_config.NumberColumn('Usuários', format='%d'),
                            'conversions': st.column_config.NumberColumn('Conversões', format='%d')
                        }
                    )

            # Device breakdown
            devices = cross_data.get('devices', {})
            if devices:
                st.markdown("#### 📱 Dispositivos")
                device_cols = st.columns(len(devices))
                device_icons = {'mobile': '📱', 'desktop': '💻', 'tablet': '📋'}
                total_dev = sum(devices.values())
                for i, (device, sess) in enumerate(devices.items()):
                    pct = (sess / total_dev * 100) if total_dev > 0 else 0
                    with device_cols[i]:
                        st.metric(
                            f"{device_icons.get(device.lower(), '📊')} {device.capitalize()}",
                            f"{sess:,}",
                            f"{pct:.1f}%"
                        )

            # Top landing pages
            landing_pages = cross_data.get('landing_pages', [])
            if landing_pages:
                st.markdown("#### 🎯 Landing Pages (Conversão)")
                lp_df = pd.DataFrame(landing_pages)
                if not lp_df.empty:
                    st.dataframe(
                        lp_df.head(5),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'path': 'Página',
                            'sessions': st.column_config.NumberColumn('Sessões', format='%d'),
                            'conversions': st.column_config.NumberColumn('Conversões', format='%d'),
                            'conversion_rate': st.column_config.NumberColumn('Taxa Conv.', format='%.2f%%'),
                            'bounce_rate': st.column_config.NumberColumn('Bounce Rate', format='%.1f%%')
                        }
                    )

        # ========== TAB 4: IMPROVEMENTS ==========
        with tab4:
            st.markdown("### 💡 Melhorias Sugeridas")
            st.markdown("*Priorizadas por impacto potencial no ROAS*")

            if suggestions:
                for i, suggestion in enumerate(suggestions):
                    priority_colors = {'high': '#EF4444', 'medium': '#F59E0B', 'low': '#3B82F6'}
                    priority_labels = {'high': 'ALTA', 'medium': 'MÉDIA', 'low': 'BAIXA'}

                    st.markdown(f"""
                    <div class="ai-card" style="border-left: 4px solid {priority_colors[suggestion['priority']]};">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div class="ai-card-title">{suggestion['icon']} {suggestion['title']}</div>
                            <span style="background: {priority_colors[suggestion['priority']]}22; color: {priority_colors[suggestion['priority']]}; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                                {priority_labels[suggestion['priority']]}
                            </span>
                        </div>
                        <div style="display: flex; gap: 20px; margin: 12px 0;">
                            <div style="background: #0F172A; padding: 8px 12px; border-radius: 6px;">
                                <span style="color: #94A3B8; font-size: 10px;">ATUAL</span><br>
                                <span style="color: #F8FAFC; font-weight: bold;">{suggestion['current']}</span>
                            </div>
                            <div style="color: #64748B; font-size: 20px; align-self: center;">→</div>
                            <div style="background: rgba(16, 185, 129, 0.1); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: #10B981; font-size: 10px;">META</span><br>
                                <span style="color: #10B981; font-weight: bold;">{suggestion['target']}</span>
                            </div>
                        </div>
                        <div class="ai-card-body">
                            <strong>Ações Recomendadas:</strong><br>
                            {'<br>'.join([f'• {action}' for action in suggestion['actions']])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 Excelente! Todas as métricas estão dentro dos limites saudáveis.")

        # ========== TAB 5: CAMPAIGNS ==========
        with tab5:
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

        # ========== TAB 6: AI CONSULTANT CHAT ==========
        with tab6:
            st.markdown("### 🤖 AI Consultant - Traffic Agent")
            st.markdown("*Pergunte sobre suas campanhas, criativos, audiências, ou estratégias de scale*")

            # Chat container with custom styling
            st.markdown("""
            <style>
            .chat-container {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                max-height: 400px;
                overflow-y: auto;
            }
            .chat-message {
                padding: 12px 16px;
                border-radius: 12px;
                margin-bottom: 12px;
                max-width: 80%;
            }
            .chat-user {
                background: #0066FF;
                color: #FFFFFF;
                margin-left: auto;
                text-align: right;
            }
            .chat-ai {
                background: #0F172A;
                color: #F8FAFC;
                border: 1px solid #334155;
            }
            .chat-ai-name {
                font-size: 11px;
                color: #60A5FA;
                margin-bottom: 4px;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)

            # Display chat history
            if st.session_state.ai_chat_history:
                for msg in st.session_state.ai_chat_history:
                    if msg['role'] == 'user':
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                            <div class="chat-message chat-user">
                                {msg['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 12px;">
                            <div class="chat-message chat-ai">
                                <div class="chat-ai-name">🤖 Traffic Agent</div>
                                {msg['content'].replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Quick question buttons
            st.markdown("#### 💬 Perguntas Rápidas")
            quick_q_cols = st.columns(4)

            quick_questions = [
                "Como está meu ROAS?",
                "Devo escalar agora?",
                "Meus criativos estão bons?",
                "Minha audiência está saturada?"
            ]

            for i, q in enumerate(quick_questions):
                with quick_q_cols[i]:
                    if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                        # Add user message
                        st.session_state.ai_chat_history.append({'role': 'user', 'content': q})

                        # Generate and add AI response
                        response = generate_ai_response(q, metrics_3d, metrics_7d, cross_data, suggestions)
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': response})

                        st.rerun()

            # Free text input
            st.markdown("---")
            with st.form(key="ai_chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Sua pergunta:",
                    placeholder="Ex: Como melhorar meu CTR? / Devo pausar alguma campanha? / Como reduzir meu CPA?",
                    key="ai_chat_input_field"
                )
                col1, col2 = st.columns([4, 1])
                with col2:
                    submit = st.form_submit_button("Enviar 📤", use_container_width=True)

                if submit and user_input:
                    # Add user message
                    st.session_state.ai_chat_history.append({'role': 'user', 'content': user_input})

                    # Generate and add AI response
                    response = generate_ai_response(user_input, metrics_3d, metrics_7d, cross_data, suggestions)
                    st.session_state.ai_chat_history.append({'role': 'assistant', 'content': response})

                    st.rerun()

            # Clear chat button
            if st.session_state.ai_chat_history:
                if st.button("🗑️ Limpar Conversa", key="clear_chat"):
                    st.session_state.ai_chat_history = []
                    st.rerun()

            # Context summary
            with st.expander("📊 Contexto Atual (dados que a IA está usando)"):
                st.markdown(f"""
                **Período:** Últimos 7 dias

                **Métricas Principais:**
                - ROAS: {metrics_7d['roas']:.2f}x
                - Gasto: ${metrics_7d['spend']:,.2f}
                - Faturamento: ${metrics_7d['revenue']:,.2f}
                - Vendas: {metrics_7d['purchases']}
                - CPA: ${metrics_7d['cpa']:.2f}

                **Engajamento:**
                - CTR: {metrics_7d['ctr']:.2f}%
                - Hook Rate: {metrics_7d['hook_rate']:.2f}%
                - Frequência: {metrics_7d['frequency']:.2f}

                **Google Analytics:**
                - Sessões: {cross_data.get('ga_sessions', 0):,}
                - Bounce Rate: {cross_data.get('ga_bounce_rate', 0):.1f}%
                - True ROAS (GA): {cross_data.get('true_roas', 0):.2f}x
                """)

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
st.markdown(f"<p style='text-align: center; color: #64748B !important; font-size: 12px;'>Adlytics v4.0.0 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)
