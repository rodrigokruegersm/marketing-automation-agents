"""
ADLYTICS - Intelligence for Scale
Marketing automation platform with AI-powered agents
Checkout integrations (Whop, ClickFunnels) + Hyros attribution
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    CampaignParser, ClientRegistry, FunnelRegistry, DataAggregator,
    ProductRegistry, WhopAdapter, ClickFunnelsAdapter, HyrosAdapter
)
from dashboard.components.integrations import get_integration_styles
from dashboard.components.creative_studio import render_creative_studio, get_creative_studio_styles
from dashboard.auth import check_password, logout

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Adlytics - Intelligence for Scale",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# AUTHENTICATION
# =============================================================================

if not check_password():
    st.stop()

# Expand sidebar after login
st.session_state["sidebar_state"] = "expanded"

# =============================================================================
# STYLES
# =============================================================================

st.markdown("""
<style>
    /* ============================================
       ADLYTICS - Dark Mode Theme
       Intelligence for Scale
       ============================================ */

    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base - Dark Background */
    .stApp {
        background: linear-gradient(135deg, #0A1628 0%, #1E293B 100%) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1600px !important;
    }

    /* ============================================
       TYPOGRAPHY - White text on dark bg
       ============================================ */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }
    p, span, div, label {
        color: #F8FAFC !important;
    }
    h1 { font-size: 1.75rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    h2 { font-size: 1.125rem !important; font-weight: 600 !important; margin-top: 1.25rem !important; }
    h3 { font-size: 0.95rem !important; font-weight: 600 !important; }

    /* ============================================
       METRICS CARDS - Dark bg, white text
       ============================================ */
    [data-testid="stMetric"] {
        background: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {
        color: #94A3B8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ============================================
       BUTTONS - Blue bg, white text
       ============================================ */
    .stButton > button {
        background: #0066FF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 102, 255, 0.3) !important;
    }
    .stButton > button:hover {
        background: #0052CC !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0, 102, 255, 0.4) !important;
    }

    /* ============================================
       FUNNEL PILLS
       ============================================ */
    .funnel-pill {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    .funnel-pill-active {
        background: #0066FF;
        color: #FFFFFF !important;
    }
    .funnel-pill-inactive {
        background: #1E293B;
        border: 1px solid #475569;
        color: #94A3B8 !important;
    }
    .funnel-pill:hover {
        border-color: #0066FF;
    }

    /* ============================================
       CARDS - Dark bg, white text
       ============================================ */
    .command-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        color: #FFFFFF !important;
    }
    .command-card h3, .command-card h4, .command-card p, .command-card span {
        color: #FFFFFF !important;
    }

    /* ============================================
       FUNNEL CARDS - Dark bg, white text
       ============================================ */
    .funnel-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s;
        color: #FFFFFF !important;
    }
    .funnel-card h3, .funnel-card h4, .funnel-card p, .funnel-card span {
        color: #FFFFFF !important;
    }
    .funnel-card:hover {
        border-color: #0066FF;
        box-shadow: 0 4px 16px rgba(0, 102, 255, 0.2);
    }
    .funnel-card-critical { border-left: 4px solid #EF4444; }
    .funnel-card-warning { border-left: 4px solid #F59E0B; }
    .funnel-card-healthy { border-left: 4px solid #10B981; }

    /* ============================================
       AI SUGGESTION BOXES - Dark colored bg, white text
       ============================================ */
    .ai-suggestion {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3B82F6;
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        color: #FFFFFF !important;
    }
    .ai-suggestion h3, .ai-suggestion h4, .ai-suggestion p, .ai-suggestion span {
        color: #FFFFFF !important;
    }
    .ai-suggestion-critical {
        background: rgba(239, 68, 68, 0.15);
        border-color: #EF4444;
        color: #FFFFFF !important;
    }
    .ai-suggestion-critical h3, .ai-suggestion-critical h4, .ai-suggestion-critical p, .ai-suggestion-critical span {
        color: #FFFFFF !important;
    }
    .ai-suggestion-opportunity {
        background: rgba(16, 185, 129, 0.15);
        border-color: #10B981;
        color: #FFFFFF !important;
    }
    .ai-suggestion-opportunity h3, .ai-suggestion-opportunity h4, .ai-suggestion-opportunity p, .ai-suggestion-opportunity span {
        color: #FFFFFF !important;
    }

    /* ============================================
       CAMPAIGN ROW - Dark bg, white text
       ============================================ */
    .campaign-row {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #FFFFFF !important;
    }
    .campaign-row h3, .campaign-row h4, .campaign-row p, .campaign-row span {
        color: #FFFFFF !important;
    }

    /* Status Badges - Bright colors on dark */
    .status-active { color: #34D399 !important; font-weight: 600; }
    .status-paused { color: #FBBF24 !important; font-weight: 600; }
    .status-error { color: #F87171 !important; font-weight: 600; }

    /* ============================================
       SIDEBAR - Dark bg, white text
       ============================================ */
    [data-testid="stSidebar"] {
        background: #0A1628 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #1E293B !important;
        border-color: #475569 !important;
    }
    [data-testid="stSidebar"] .stSelectbox * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* ============================================
       MAIN AREA SELECTBOX - Dark bg, white text
       ============================================ */
    .stSelectbox > div > div {
        background: #1E293B !important;
        border-color: #475569 !important;
        border-radius: 8px !important;
    }
    .stSelectbox * {
        color: #FFFFFF !important;
    }

    /* ============================================
       TABS - Dark bg, white/blue text
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 0.5rem !important;
        border-bottom: 1px solid #475569 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 0 !important;
        color: #94A3B8 !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #0066FF !important;
        border-bottom: 2px solid #0066FF !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden !important; }

    /* ============================================
       ALERTS - Dark bg, white text
       ============================================ */
    .stAlert {
        background: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    .stAlert * {
        color: #FFFFFF !important;
    }

    /* ============================================
       INTEGRATION CARDS - Dark bg, white text
       ============================================ */
    .integration-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        color: #FFFFFF !important;
    }
    .integration-card h3, .integration-card h4, .integration-card p, .integration-card span {
        color: #FFFFFF !important;
    }
    .integration-connected { border-left: 4px solid #10B981; }
    .integration-disconnected { border-left: 4px solid #EF4444; }

    /* ============================================
       PRODUCT CARD - Dark bg, white text
       ============================================ */
    .product-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        color: #FFFFFF !important;
    }
    .product-card h3, .product-card h4, .product-card p, .product-card span {
        color: #FFFFFF !important;
    }
    .platform-badge {
        background: #0066FF;
        color: #FFFFFF !important;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }

    /* ============================================
       CPP ANALYSIS - Dark colored bg, white text
       ============================================ */
    .cpp-analysis {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #FFFFFF !important;
    }
    .cpp-analysis h3, .cpp-analysis h4, .cpp-analysis p, .cpp-analysis span {
        color: #FFFFFF !important;
    }
    .cpp-excellent {
        border-left: 4px solid #10B981;
        background: rgba(16, 185, 129, 0.15);
    }
    .cpp-excellent h3, .cpp-excellent h4, .cpp-excellent p, .cpp-excellent span {
        color: #FFFFFF !important;
    }
    .cpp-good {
        border-left: 4px solid #10B981;
        background: #1E293B;
    }
    .cpp-warning {
        border-left: 4px solid #F59E0B;
        background: rgba(245, 158, 11, 0.15);
    }
    .cpp-warning h3, .cpp-warning h4, .cpp-warning p, .cpp-warning span {
        color: #FFFFFF !important;
    }
    .cpp-critical {
        border-left: 4px solid #EF4444;
        background: rgba(239, 68, 68, 0.15);
    }
    .cpp-critical h3, .cpp-critical h4, .cpp-critical p, .cpp-critical span {
        color: #FFFFFF !important;
    }
    .cpp-threshold {
        background: #0A1628;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #475569;
        color: #FFFFFF !important;
    }

    /* ============================================
       CHECKOUT SALES CARD - Dark bg, white text
       ============================================ */
    .checkout-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        color: #FFFFFF !important;
    }
    .checkout-card h3, .checkout-card h4, .checkout-card p, .checkout-card span {
        color: #FFFFFF !important;
    }

    /* ============================================
       HYROS ATTRIBUTION - Dark blue-tinted bg, white text
       ============================================ */
    .hyros-card {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3B82F6;
        border-radius: 12px;
        padding: 1.25rem;
        color: #FFFFFF !important;
    }
    .hyros-card h3, .hyros-card h4, .hyros-card p, .hyros-card span {
        color: #FFFFFF !important;
    }

    /* ============================================
       LOGO HEADER
       ============================================ */
    .adlytics-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    .adlytics-logo {
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .adlytics-logo-ad { color: #0066FF !important; }
    .adlytics-logo-lytics { color: #FFFFFF !important; }
    .adlytics-tagline {
        color: #94A3B8 !important;
        font-size: 0.875rem;
        font-weight: 400;
    }

    /* ============================================
       EXPANDER - Dark bg, white text
       ============================================ */
    .streamlit-expanderHeader {
        background: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    .streamlit-expanderHeader * {
        color: #FFFFFF !important;
    }
    .streamlit-expanderContent {
        background: #1E293B !important;
        color: #FFFFFF !important;
    }
    .streamlit-expanderContent * {
        color: #FFFFFF !important;
    }

    /* ============================================
       TEXT INPUT - Dark bg, white text
       ============================================ */
    .stTextInput > div > div > input {
        background: #1E293B !important;
        color: #FFFFFF !important;
        border-color: #475569 !important;
    }
    .stTextInput label {
        color: #FFFFFF !important;
    }

    /* ============================================
       DATE INPUT - Dark bg, white text
       ============================================ */
    .stDateInput > div > div > input {
        background: #1E293B !important;
        color: #FFFFFF !important;
        border-color: #475569 !important;
    }

    /* ============================================
       DATAFRAME/TABLE - Dark bg, white text
       ============================================ */
    .stDataFrame {
        background: #1E293B !important;
    }
    .stDataFrame * {
        color: #FFFFFF !important;
    }

    /* ============================================
       CAPTION - Muted text
       ============================================ */
    .stCaption, .stCaption * {
        color: #94A3B8 !important;
    }

    /* ============================================
       INFO/WARNING/ERROR BOXES - Dark theme
       ============================================ */
    .stInfo {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
    }
    .stInfo * {
        color: #FFFFFF !important;
    }
    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid #F59E0B !important;
    }
    .stWarning * {
        color: #FFFFFF !important;
    }
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid #EF4444 !important;
    }
    .stError * {
        color: #FFFFFF !important;
    }
    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid #10B981 !important;
    }
    .stSuccess * {
        color: #FFFFFF !important;
    }

    /* ============================================
       SPINNER - Blue color
       ============================================ */
    .stSpinner > div {
        border-color: #0066FF transparent transparent transparent !important;
    }

    /* ============================================
       PLOTLY CHARTS - Dark theme
       ============================================ */
    .js-plotly-plot .plotly .bg {
        fill: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# Add integration-specific styles
st.markdown(get_integration_styles(), unsafe_allow_html=True)

# Add Creative Studio styles
st.markdown(get_creative_studio_styles(), unsafe_allow_html=True)

# =============================================================================
# API CONFIGURATION
# =============================================================================

def get_client_credentials(client_slug: str = None):
    """Get API credentials for a client"""
    token = ""
    account_id = ""

    # Try Streamlit secrets first
    try:
        if client_slug:
            token = st.secrets.get(f"{client_slug.upper()}_META_ACCESS_TOKEN", "")
            account_id = st.secrets.get(f"{client_slug.upper()}_META_AD_ACCOUNT_ID", "")

        if not token:
            token = st.secrets.get("META_ACCESS_TOKEN", "")
        if not account_id:
            account_id = st.secrets.get("META_AD_ACCOUNT_ID", "")
    except Exception:
        pass

    # Fallback to direct secrets access
    if not token:
        try:
            token = st.secrets["META_ACCESS_TOKEN"]
        except (KeyError, FileNotFoundError):
            token = os.getenv('META_ACCESS_TOKEN', '')

    if not account_id:
        try:
            account_id = st.secrets["META_AD_ACCOUNT_ID"]
        except (KeyError, FileNotFoundError):
            account_id = os.getenv('META_AD_ACCOUNT_ID', '')

    return {'token': token, 'account_id': account_id}


def get_checkout_credentials():
    """Get checkout platform credentials"""
    try:
        return {
            'whop': {
                'api_key': st.secrets.get("WHOP_API_KEY", os.getenv("WHOP_API_KEY", "")),
                'company_id': st.secrets.get("WHOP_COMPANY_ID", os.getenv("WHOP_COMPANY_ID", ""))
            },
            'clickfunnels': {
                'api_key': st.secrets.get("CLICKFUNNELS_API_KEY", os.getenv("CLICKFUNNELS_API_KEY", "")),
                'workspace_id': st.secrets.get("CLICKFUNNELS_WORKSPACE_ID", os.getenv("CLICKFUNNELS_WORKSPACE_ID", ""))
            }
        }
    except:
        return {
            'whop': {'api_key': '', 'company_id': ''},
            'clickfunnels': {'api_key': '', 'workspace_id': ''}
        }


def get_hyros_credentials():
    """Get Hyros credentials"""
    try:
        return {
            'api_key': st.secrets.get("HYROS_API_KEY", os.getenv("HYROS_API_KEY", ""))
        }
    except:
        return {'api_key': ''}


API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

# =============================================================================
# INITIALIZE CORE MODULES
# =============================================================================

@st.cache_resource
def init_registries():
    """Initialize client and funnel registries"""
    client_registry = ClientRegistry()
    funnel_registry = FunnelRegistry()
    product_registry = ProductRegistry()
    return client_registry, funnel_registry, product_registry


@st.cache_resource
def get_campaign_parser():
    """Get campaign parser instance"""
    return CampaignParser()


@st.cache_resource
def init_checkout_adapters():
    """Initialize checkout platform adapters"""
    creds = get_checkout_credentials()
    adapters = {}

    if creds['whop']['api_key']:
        adapters['whop'] = WhopAdapter(
            api_key=creds['whop']['api_key'],
            company_id=creds['whop']['company_id']
        )

    if creds['clickfunnels']['api_key']:
        adapters['clickfunnels'] = ClickFunnelsAdapter(
            api_key=creds['clickfunnels']['api_key'],
            workspace_id=creds['clickfunnels']['workspace_id']
        )

    return adapters


@st.cache_resource
def init_hyros_adapter():
    """Initialize Hyros adapter"""
    creds = get_hyros_credentials()
    if creds['api_key']:
        return HyrosAdapter(api_key=creds['api_key'])
    return None

# =============================================================================
# API FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def fetch_account_insights(account_id: str, token: str, date_preset='last_7d', start_date=None, end_date=None):
    """Fetch account-level insights"""
    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        'fields': 'spend,impressions,reach,frequency,cpm,clicks,cpc,ctr,actions,action_values,cost_per_action_type,purchase_roas',
        'access_token': token
    }

    if start_date and end_date:
        params['time_range'] = json.dumps({
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d')
        })
    else:
        params['date_preset'] = date_preset

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('data', [{}])[0] if 'data' in data else None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


@st.cache_data(ttl=60)
def fetch_campaigns(account_id: str, token: str):
    """Fetch all campaigns with their status and metrics"""
    url = f"{BASE_URL}/{account_id}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status,daily_budget,lifetime_budget,objective,insights.date_preset(last_7d){spend,impressions,clicks,actions,action_values,purchase_roas}',
        'limit': 100,
        'access_token': token
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        # Check for API errors
        if 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            error_code = data['error'].get('code', 'N/A')
            st.error(f"Meta API Error ({error_code}): {error_msg}")
            return []
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching campaigns: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_checkout_metrics(_adapter, platform_name: str, start_date=None, end_date=None):
    """Fetch checkout metrics from adapter"""
    try:
        metrics = _adapter.get_metrics(start_date=start_date, end_date=end_date)
        return metrics.to_dict() if hasattr(metrics, 'to_dict') else {}
    except Exception as e:
        return {'error': str(e)}


@st.cache_data(ttl=300)
def fetch_hyros_attribution(_adapter, start_date=None, end_date=None):
    """Fetch Hyros attribution data"""
    try:
        return _adapter.get_attribution_summary(start_date=start_date, end_date=end_date)
    except Exception as e:
        return {'error': str(e)}


def update_campaign_status(campaign_id: str, status: str, token: str):
    """Update campaign status (ACTIVE/PAUSED)"""
    url = f"{BASE_URL}/{campaign_id}"
    params = {'status': status, 'access_token': token}
    try:
        response = requests.post(url, params=params)
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def update_budget(entity_id: str, budget_cents: int, token: str, budget_type='daily_budget'):
    """Update budget (in cents)"""
    url = f"{BASE_URL}/{entity_id}"
    params = {budget_type: budget_cents, 'access_token': token}
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
        'leads': extract_action_value(actions, 'lead'),
    }


def generate_ai_suggestions(metrics, parsed_campaigns, funnel_tag=None, product_data=None):
    """Generate AI-powered optimization suggestions with product awareness"""
    suggestions = []

    if not metrics:
        return suggestions

    funnel_context = f" no funil {{{funnel_tag}}}" if funnel_tag else ""

    # Product-aware CPP Analysis
    if product_data and metrics['cpp'] > 0:
        breakeven = product_data.get('breakeven_cpp', 0)
        target = product_data.get('target_cpp', 0)
        product_price = product_data.get('price', 0)

        if breakeven > 0:
            if metrics['cpp'] > breakeven:
                excess = metrics['cpp'] - breakeven
                suggestions.append({
                    'type': 'critical',
                    'icon': '🚨',
                    'title': f'CPP ACIMA DO BREAKEVEN{funnel_context}',
                    'message': f"CPP: ${metrics['cpp']:.2f} | Breakeven: ${breakeven:.2f} | Excesso: ${excess:.2f}. PAUSAR campanhas ineficientes URGENTE!",
                    'priority': 0
                })
            elif metrics['cpp'] > breakeven * 0.8:
                margin = breakeven - metrics['cpp']
                suggestions.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': f'CPP Proximo do Limite{funnel_context}',
                    'message': f"CPP: ${metrics['cpp']:.2f} | Margem de apenas ${margin:.2f} ate breakeven.",
                    'priority': 1
                })
            elif target > 0 and metrics['cpp'] <= target:
                room = target - metrics['cpp']
                suggestions.append({
                    'type': 'opportunity',
                    'icon': '🚀',
                    'title': f'CPP Excelente - Escalar!{funnel_context}',
                    'message': f"CPP: ${metrics['cpp']:.2f} | Target: ${target:.2f} | ${room:.2f} abaixo do target. Produto: ${product_price:.0f}. Aumentar budget 20-30%!",
                    'priority': 2
                })
    else:
        if metrics['cpp'] > 25:
            suggestions.append({
                'type': 'critical',
                'icon': '💸',
                'title': f'CPP Muito Alto{funnel_context}',
                'message': f"Custo por compra: ${metrics['cpp']:.2f}. Revisar ad sets com CPP acima de $20.",
                'priority': 1
            })
        elif metrics['cpp'] <= 12 and metrics['cpp'] > 0:
            suggestions.append({
                'type': 'opportunity',
                'icon': '💎',
                'title': f'CPP Excelente{funnel_context}',
                'message': f"CPP: ${metrics['cpp']:.2f}. Identificar ad sets com melhor CPP e aumentar budget.",
                'priority': 2
            })

    # ROAS Analysis
    if metrics['roas'] < 1.5:
        suggestions.append({
            'type': 'critical',
            'icon': '🚨',
            'title': f'ROAS Critico{funnel_context}',
            'message': f"ROAS atual: {metrics['roas']:.2f}x (abaixo de 1.5x). Pausar campanhas de baixo desempenho.",
            'priority': 1
        })
    elif metrics['roas'] >= 2.5:
        suggestions.append({
            'type': 'opportunity',
            'icon': '🚀',
            'title': f'Oportunidade de Escala{funnel_context}',
            'message': f"ROAS forte: {metrics['roas']:.2f}x. Aumentar budget em 20-30%.",
            'priority': 2
        })

    # Frequency Analysis
    if metrics['frequency'] > 3:
        suggestions.append({
            'type': 'critical',
            'icon': '🔄',
            'title': f'Frequencia Alta{funnel_context}',
            'message': f"Frequencia: {metrics['frequency']:.2f}. Audiencia saturada. Subir novos criativos.",
            'priority': 1
        })

    # CTR Analysis
    if metrics['ctr'] < 1:
        suggestions.append({
            'type': 'warning',
            'icon': '👆',
            'title': f'CTR Baixo{funnel_context}',
            'message': f"CTR: {metrics['ctr']:.2f}%. Testar novos hooks.",
            'priority': 3
        })
    elif metrics['ctr'] >= 3:
        suggestions.append({
            'type': 'opportunity',
            'icon': '🎯',
            'title': f'CTR Alto{funnel_context}',
            'message': f"CTR: {metrics['ctr']:.2f}%. Duplicar para novos publicos.",
            'priority': 3
        })

    suggestions.sort(key=lambda x: x['priority'])
    return suggestions


def render_cpp_analysis_card(cpp: float, product_data: dict):
    """Render product-aware CPP analysis card"""
    if not product_data or cpp <= 0:
        return

    price = product_data.get('price', 0)
    breakeven = product_data.get('breakeven_cpp', 0)
    target = product_data.get('target_cpp', 0)
    product_name = product_data.get('name', 'Produto')

    if cpp <= target:
        status_class, status_icon, status_text = "cpp-excellent", "🟢", "EXCELENTE"
        msg = f"${target - cpp:.2f} abaixo do target - ESCALAR!"
    elif cpp <= breakeven:
        status_class, status_icon, status_text = "cpp-good", "🟢", "SAUDAVEL"
        msg = f"Margem de ${breakeven - cpp:.2f} ate breakeven"
    elif cpp <= breakeven * 1.2:
        status_class, status_icon, status_text = "cpp-warning", "🟡", "ATENCAO"
        msg = f"${cpp - breakeven:.2f} acima do breakeven - Otimizar"
    else:
        status_class, status_icon, status_text = "cpp-critical", "🔴", "CRITICO"
        msg = f"${cpp - breakeven:.2f} ACIMA DO BREAKEVEN - PAUSAR!"

    st.markdown(f"""
    <div class="cpp-analysis {status_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">{status_icon} CPP: {status_text}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{msg}</p>
                <small style="opacity: 0.7;">{product_name}</small>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.5rem; font-weight: bold;">${cpp:.2f}</div>
                <small>CPP Atual</small>
            </div>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;">
            <div class="cpp-threshold"><small>Produto</small><br><strong>${price:,.0f}</strong></div>
            <div class="cpp-threshold"><small>Target CPP</small><br><strong style="color: #10B981;">${target:.2f}</strong></div>
            <div class="cpp-threshold"><small>Breakeven</small><br><strong style="color: #F59E0B;">${breakeven:.2f}</strong></div>
            <div class="cpp-threshold"><small>Margem</small><br><strong>${abs(breakeven - cpp):.2f}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None
if 'selected_funnel' not in st.session_state:
    st.session_state.selected_funnel = None
if 'date_preset' not in st.session_state:
    st.session_state.date_preset = 'last_7d'
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <div class="adlytics-logo">
            <span class="adlytics-logo-ad">Ad</span><span class="adlytics-logo-lytics">lytics</span>
        </div>
        <div class="adlytics-tagline">Intelligence for Scale</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Date Period Selector
    st.markdown("### 📅 Periodo")
    date_options = {
        'today': 'Hoje', 'yesterday': 'Ontem', 'last_7d': 'Ultimos 7 dias',
        'last_14d': 'Ultimos 14 dias', 'last_30d': 'Ultimos 30 dias',
        'this_month': 'Este mes', 'last_month': 'Mes passado', 'custom': 'Personalizado'
    }

    date_preset = st.selectbox("Periodo", options=list(date_options.keys()), index=2,
                               format_func=lambda x: date_options.get(x, x), label_visibility="collapsed")

    custom_start, custom_end = None, None
    if date_preset == 'custom':
        col_s, col_e = st.columns(2)
        with col_s:
            custom_start = st.date_input("De", value=datetime.now() - timedelta(days=7), label_visibility="collapsed")
        with col_e:
            custom_end = st.date_input("Ate", value=datetime.now(), label_visibility="collapsed")

    st.markdown("---")

    # Integration Status
    st.markdown("### 🔌 Integracoes")
    checkout_adapters = init_checkout_adapters()
    hyros_adapter = init_hyros_adapter()

    integrations = {
        'Meta Ads': {'connected': bool(get_client_credentials()['token']), 'icon': '📊'},
        'Whop': {'connected': 'whop' in checkout_adapters, 'icon': '🌐'},
        'ClickFunnels': {'connected': 'clickfunnels' in checkout_adapters, 'icon': '🔵'},
        'Hyros': {'connected': hyros_adapter is not None, 'icon': '📈'}
    }

    for name, status in integrations.items():
        icon = "🟢" if status['connected'] else "⚪"
        st.markdown(f"{status['icon']} {name}: {icon}")

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Acoes")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("⚙️ Config", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

    st.markdown("---")
    st.caption(f"Adlytics v2.0 · {datetime.now().strftime('%H:%M')}")

# =============================================================================
# MAIN CONTENT
# =============================================================================

credentials = get_client_credentials(st.session_state.selected_client)
META_ACCESS_TOKEN = credentials['token']
META_AD_ACCOUNT_ID = credentials['account_id']

st.markdown("""
<div class="adlytics-header">
    <span class="adlytics-logo"><span class="adlytics-logo-ad">Ad</span><span class="adlytics-logo-lytics">lytics</span></span>
    <span class="adlytics-tagline">| Dashboard</span>
</div>
""", unsafe_allow_html=True)

# Settings Panel
if st.session_state.show_settings:
    st.markdown("## ⚙️ Configuracoes")
    with st.expander("Meta Ads", expanded=True):
        st.text_input("Access Token", type="password", key="s_meta_token")
        st.text_input("Ad Account ID", key="s_meta_account")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Whop"):
            st.text_input("API Key", type="password", key="s_whop_key")
            st.text_input("Company ID", key="s_whop_company")
    with c2:
        with st.expander("ClickFunnels"):
            st.text_input("API Key", type="password", key="s_cf_key")
            st.text_input("Workspace ID", key="s_cf_workspace")
    with st.expander("Hyros"):
        st.text_input("API Key", type="password", key="s_hyros_key")
    st.info("Configure credenciais nos Secrets do Streamlit ou variaveis de ambiente.")
    st.markdown("---")

if META_ACCESS_TOKEN and META_AD_ACCOUNT_ID:
    # Debug info (collapsible)
    with st.expander("🔧 Debug Info", expanded=False):
        st.write(f"**Account ID:** {META_AD_ACCOUNT_ID}")
        st.write(f"**Token (last 10 chars):** ...{META_ACCESS_TOKEN[-10:] if len(META_ACCESS_TOKEN) > 10 else 'N/A'}")

    client_registry, funnel_registry, product_registry = init_registries()

    with st.spinner("Carregando..."):
        raw_campaigns = fetch_campaigns(META_AD_ACCOUNT_ID, META_ACCESS_TOKEN)

    if raw_campaigns:
        parser = get_campaign_parser()
        parsed_campaigns = parser.parse_campaigns(raw_campaigns)

        client_slug = st.session_state.selected_client or "brez-scales"
        try:
            product_registry.load_client_products(client_slug)
        except:
            pass

        # Funnel Pills
        st.markdown("### 🎯 Filtrar por Funil")
        all_funnels = ["Todos"] + list(parser.funnels.keys())
        cols = st.columns(min(len(all_funnels), 8))

        for idx, funnel in enumerate(all_funnels[:8]):
            with cols[idx]:
                is_selected = (funnel == "Todos" and not st.session_state.selected_funnel) or (funnel == st.session_state.selected_funnel)
                if funnel != "Todos":
                    active = sum(1 for c in parser.funnels.get(funnel, []) if c.is_active)
                    label = f"{{{funnel}}} ({active})"
                else:
                    label = f"📊 Todos ({len(parsed_campaigns)})"
                if st.button(label, key=f"f_{funnel}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    st.session_state.selected_funnel = None if funnel == "Todos" else funnel
                    st.rerun()

        st.markdown("---")

        display_campaigns = parser.get_campaigns_by_funnel(st.session_state.selected_funnel) if st.session_state.selected_funnel else parsed_campaigns

        funnel_product_data = None
        if st.session_state.selected_funnel:
            product = product_registry.get_product_for_funnel(st.session_state.selected_funnel)
            if product:
                funnel_product_data = {'name': product.name, 'price': product.price,
                                       'breakeven_cpp': product.breakeven_cpp, 'target_cpp': product.target_cpp}

        with st.spinner("Carregando metricas..."):
            if date_preset == 'custom' and custom_start and custom_end:
                raw_data = fetch_account_insights(META_AD_ACCOUNT_ID, META_ACCESS_TOKEN, start_date=custom_start, end_date=custom_end)
            else:
                raw_data = fetch_account_insights(META_AD_ACCOUNT_ID, META_ACCESS_TOKEN, date_preset=date_preset)
            metrics = parse_metrics(raw_data)

        if metrics:
            # KPI Overview
            funnel_label = f" | {{{st.session_state.selected_funnel}}}" if st.session_state.selected_funnel else ""
            st.markdown(f"### 📊 Metricas{funnel_label}")

            k1, k2, k3, k4, k5, k6 = st.columns(6)
            with k1:
                roas_d = "🟢 Bom" if metrics['roas'] >= 2 else ("🟡" if metrics['roas'] >= 1.5 else "🔴 Critico")
                st.metric("ROAS", f"{metrics['roas']:.2f}x", roas_d)
            with k2:
                st.metric("Revenue", f"${metrics['revenue']:,.0f}", f"${metrics['profit']:,.0f}")
            with k3:
                st.metric("Ad Spend", f"${metrics['spend']:,.0f}")
            with k4:
                if funnel_product_data:
                    be = funnel_product_data['breakeven_cpp']
                    cpp_d = f"🟢 <${be:.0f}" if metrics['cpp'] <= be else f"🔴 >${be:.0f}"
                else:
                    cpp_d = "🟢" if metrics['cpp'] <= 15 else ("🟡" if metrics['cpp'] <= 20 else "🔴")
                st.metric("CPP", f"${metrics['cpp']:.2f}", cpp_d)
            with k5:
                st.metric("Purchases", f"{int(metrics['purchases'])}")
            with k6:
                freq_d = "🟢" if metrics['frequency'] <= 2 else ("🟡" if metrics['frequency'] <= 2.5 else "🔴")
                st.metric("Frequency", f"{metrics['frequency']:.2f}", freq_d)

            if funnel_product_data and metrics['cpp'] > 0:
                render_cpp_analysis_card(metrics['cpp'], funnel_product_data)

            st.markdown("---")

            # TABS
            tab_overview, tab_funnels, tab_checkout, tab_campaigns, tab_ai, tab_creative = st.tabs([
                "📊 Overview", "🎯 Funis", "💰 Checkout", "📢 Campanhas", "🤖 IA", "🎬 Criativos"
            ])

            with tab_overview:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("### 🔄 Funil de Conversao")
                    fig = go.Figure(go.Funnel(
                        y=['Impressions', 'Clicks', 'LP Views', 'Checkouts', 'Purchases'],
                        x=[metrics['impressions'], metrics['clicks'], int(metrics['lp_views']),
                           int(metrics['checkouts']), int(metrics['purchases'])],
                        texttemplate="%{value:,}",
                        textfont=dict(color='#0A1628'),
                        marker=dict(color=['#0066FF', '#3B82F6', '#60A5FA', '#93C5FD', '#10B981'])
                    ))
                    fig.update_layout(
                        height=350,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FFFFFF',
                        font=dict(color='#0A1628', family='Inter')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown("### 💰 Financeiro")
                    if metrics['revenue'] > 0:
                        fig2 = go.Figure(go.Pie(
                            labels=['Spend', 'Profit'],
                            values=[metrics['spend'], max(metrics['profit'], 0)],
                            hole=0.6,
                            marker_colors=['#EF4444', '#10B981'],
                            textfont=dict(color='#0A1628')
                        ))
                        fig2.update_layout(
                            height=300,
                            paper_bgcolor='#FFFFFF',
                            font=dict(color='#0A1628', family='Inter'),
                            annotations=[dict(
                                text=f"${metrics['revenue']:,.0f}",
                                x=0.5, y=0.5,
                                font_size=18,
                                showarrow=False,
                                font_color='#0A1628'
                            )]
                        )
                        st.plotly_chart(fig2, use_container_width=True)

            with tab_funnels:
                st.markdown("## 🎯 Analise por Funil")
                for tag, camps in parser.funnels.items():
                    spend = sum(c.metrics.get('spend', 0) for c in camps)
                    rev = sum(c.metrics.get('revenue', 0) for c in camps)
                    purch = sum(c.metrics.get('purchases', 0) for c in camps)
                    roas = rev / spend if spend > 0 else 0
                    cpp = spend / purch if purch > 0 else 0
                    prod = product_registry.get_product_for_funnel(tag)
                    prod_info = f" | ${prod.price:.0f}" if prod else ""
                    status = "🟢" if (prod and cpp <= prod.breakeven_cpp) or roas >= 2 else ("🔴" if (prod and cpp > prod.breakeven_cpp) or roas < 1.5 else "🟡")
                    with st.expander(f"{status} {{{tag}}} - ROAS: {roas:.2f}x | CPP: ${cpp:.2f}{prod_info}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("ROAS", f"{roas:.2f}x")
                        c2.metric("Spend", f"${spend:,.0f}")
                        c3.metric("CPP", f"${cpp:.2f}")
                        c4.metric("Purchases", f"{int(purch)}")
                        if prod:
                            if cpp <= prod.target_cpp:
                                st.success(f"CPP Excelente! ${prod.target_cpp - cpp:.2f} abaixo do target")
                            elif cpp <= prod.breakeven_cpp:
                                st.info(f"CPP OK. Margem: ${prod.breakeven_cpp - cpp:.2f}")
                            else:
                                st.error(f"CPP ACIMA do breakeven! Excesso: ${cpp - prod.breakeven_cpp:.2f}")

            with tab_checkout:
                st.markdown("## 💰 Dados de Checkout")
                checkout_adapters = init_checkout_adapters()
                if not checkout_adapters:
                    st.info("Nenhuma plataforma de checkout conectada. Configure Whop ou ClickFunnels.")
                else:
                    checkout_end = datetime.now()
                    checkout_start = checkout_end - timedelta(days=7)
                    for pname, adapter in checkout_adapters.items():
                        icon = "🌐" if pname == "whop" else "🔵"
                        with st.expander(f"{icon} {pname.upper()}", expanded=True):
                            data = fetch_checkout_metrics(adapter, pname, checkout_start, checkout_end)
                            if 'error' in data:
                                st.error(data['error'])
                            else:
                                c1, c2, c3, c4 = st.columns(4)
                                c1.metric("Vendas", data.get('total_sales', 0))
                                c2.metric("Aprovadas", data.get('approved_sales', 0))
                                c3.metric("Faturamento", f"${data.get('gross_revenue', 0):,.0f}")
                                c4.metric("Ticket Medio", f"${data.get('average_ticket', 0):,.2f}")

                    st.markdown("### 📈 Hyros Attribution")
                    hyros = init_hyros_adapter()
                    if hyros:
                        hdata = fetch_hyros_attribution(hyros, checkout_start, checkout_end)
                        if 'error' not in hdata:
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Total Sales", hdata.get('total_sales', 0))
                            c2.metric("Revenue", f"${hdata.get('total_revenue', 0):,.0f}")
                            c3.metric("Qualified", hdata.get('qualified_sales', 0))
                            c4.metric("Recurring", hdata.get('recurring_sales', 0))

                            # Show by platform breakdown
                            by_platform = hdata.get('by_platform', {})
                            if by_platform:
                                st.markdown("#### By Platform")
                                cols = st.columns(len(by_platform))
                                for idx, (platform, data) in enumerate(by_platform.items()):
                                    with cols[idx]:
                                        icon = "📘" if platform == "FACEBOOK" else ("🔍" if "GOOGLE" in platform else "🌐")
                                        st.markdown(f"""<div class="hyros-card">
                                            <h4>{icon} {platform}</h4>
                                            <p>Sales: {data.get('sales', 0)}</p>
                                            <p>Revenue: ${data.get('revenue', 0):,.0f}</p>
                                        </div>""", unsafe_allow_html=True)
                        else:
                            st.warning(f"Hyros error: {hdata.get('error', 'Unknown')}")
                    else:
                        st.info("Conecte o Hyros para atribuicao avancada.")

            with tab_campaigns:
                st.markdown("## 📢 Campanhas")
                for c in sorted(display_campaigns, key=lambda x: x.metrics.get('spend', 0), reverse=True):
                    status = "🟢" if c.is_active else "🟡"
                    spend = c.metrics.get('spend', 0)
                    roas = c.metrics.get('roas', 0)
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
                    col1.markdown(f"**{c.name[:45]}**")
                    col2.markdown(f"{status}")
                    col3.markdown(f"${spend:,.0f}")
                    col4.markdown(f"{roas:.2f}x")
                    with col5:
                        bc1, bc2 = st.columns(2)
                        if c.is_active:
                            if bc1.button("⏸️", key=f"p_{c.id}"):
                                update_campaign_status(c.id, "PAUSED", META_ACCESS_TOKEN)
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            if bc1.button("▶️", key=f"a_{c.id}"):
                                update_campaign_status(c.id, "ACTIVE", META_ACCESS_TOKEN)
                                st.cache_data.clear()
                                st.rerun()
                    st.markdown("---")

            with tab_ai:
                st.markdown("## 🤖 IA Insights")
                suggestions = generate_ai_suggestions(metrics, display_campaigns, st.session_state.selected_funnel, funnel_product_data)
                if suggestions:
                    for s in suggestions:
                        css = f"ai-suggestion ai-suggestion-{s['type']}" if s['type'] in ['critical', 'opportunity'] else "ai-suggestion"
                        st.markdown(f"""<div class="{css}"><h3>{s['icon']} {s['title']}</h3><p>{s['message']}</p></div>""", unsafe_allow_html=True)
                else:
                    st.success("✅ Metricas saudaveis!")

            with tab_creative:
                client_slug = st.session_state.selected_client or "brez-scales"
                render_creative_studio(client_slug)
        else:
            st.warning("Sem dados para este periodo.")
    else:
        st.info("Nenhuma campanha encontrada.")
else:
    st.error("❌ Configure META_ACCESS_TOKEN e META_AD_ACCOUNT_ID")

st.markdown("---")
st.caption(f"Adlytics v2.0 · {datetime.now().strftime('%Y-%m-%d %H:%M')} · Whop + Hyros Integration")
