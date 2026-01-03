"""
ADLYTICS - Intelligence for Scale
Modern dashboard with AI-powered marketing agents
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
from dashboard.auth import check_password, logout

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Adlytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# AUTHENTICATION
# =============================================================================

if not check_password():
    st.stop()

# =============================================================================
# GLOBAL STYLES
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Base */
    .stApp {
        background: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Hide Streamlit elements */
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }

    /* Navigation buttons in sidebar */
    .nav-button {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        color: #94A3B8 !important;
        background: transparent;
        border: none;
        width: 100%;
        font-size: 14px;
        font-weight: 500;
    }
    .nav-button:hover {
        background: #334155;
        color: #F8FAFC !important;
    }
    .nav-button.active {
        background: #0066FF;
        color: #FFFFFF !important;
    }
    .nav-icon {
        font-size: 20px;
        width: 24px;
        text-align: center;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 12px !important; text-transform: uppercase !important; }
    [data-testid="stMetricValue"] { color: #F8FAFC !important; font-size: 28px !important; font-weight: 600 !important; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Cards */
    .card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #334155;
    }
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #F8FAFC !important;
        margin: 0;
    }

    /* Status badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
    }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34D399 !important; }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #FBBF24 !important; }
    .badge-error { background: rgba(239, 68, 68, 0.2); color: #F87171 !important; }
    .badge-info { background: rgba(59, 130, 246, 0.2); color: #60A5FA !important; }

    /* Buttons */
    .stButton > button {
        background: #0066FF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #0052CC !important;
        transform: translateY(-1px) !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #1E293B !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
    }
    .stSelectbox label { color: #94A3B8 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 0 !important;
        border-bottom: 1px solid #334155 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #94A3B8 !important;
        padding: 12px 20px !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0066FF !important;
        border-bottom-color: #0066FF !important;
    }

    /* Data table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    .data-table th {
        text-align: left;
        padding: 12px;
        color: #94A3B8 !important;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        border-bottom: 1px solid #334155;
    }
    .data-table td {
        padding: 12px;
        color: #F8FAFC !important;
        border-bottom: 1px solid #1E293B;
    }
    .data-table tr:hover td {
        background: #1E293B;
    }

    /* Plotly charts */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }

    /* Alerts */
    .stAlert { background: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; }

    /* Logo */
    .logo { font-size: 24px; font-weight: 700; margin-bottom: 24px; padding: 0 16px; }
    .logo-ad { color: #0066FF !important; }
    .logo-lytics { color: #F8FAFC !important; }

    /* Page header */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #334155;
    }
    .page-title {
        font-size: 24px;
        font-weight: 600;
        color: #F8FAFC !important;
        margin: 0;
    }
    .page-subtitle {
        font-size: 14px;
        color: #94A3B8 !important;
        margin-top: 4px;
    }

    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
    }
    .kpi-label {
        font-size: 12px;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 600;
        color: #F8FAFC !important;
    }
    .kpi-change {
        font-size: 13px;
        margin-top: 4px;
    }
    .kpi-change.positive { color: #34D399 !important; }
    .kpi-change.negative { color: #F87171 !important; }

    /* Campaign row */
    .campaign-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    .campaign-item:hover {
        border-color: #0066FF;
    }
    .campaign-name {
        font-weight: 500;
        color: #F8FAFC !important;
    }
    .campaign-meta {
        font-size: 13px;
        color: #94A3B8 !important;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: #1E293B !important;
        border-color: #334155 !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #1E293B !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'traffic'

# =============================================================================
# API CONFIG
# =============================================================================

def get_credentials():
    """Get API credentials from secrets"""
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

API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

@st.cache_data(ttl=300)
def fetch_campaigns(account_id: str, token: str):
    """Fetch campaigns from Meta Ads"""
    if not account_id or not token:
        return []

    url = f"{BASE_URL}/{account_id}/campaigns"
    params = {
        'fields': 'id,name,status,effective_status,daily_budget,objective,insights.date_preset(last_7d){spend,impressions,clicks,actions,action_values,purchase_roas}',
        'limit': 50,
        'access_token': token
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'error' in data:
            st.error(f"Meta API: {data['error'].get('message', 'Unknown error')}")
            return []
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_account_insights(account_id: str, token: str):
    """Fetch account insights"""
    if not account_id or not token:
        return None

    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        'fields': 'spend,impressions,reach,clicks,actions,action_values,purchase_roas',
        'date_preset': 'last_7d',
        'access_token': token
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'data' in data and data['data']:
            return data['data'][0]
        return None
    except:
        return None

def parse_metrics(data):
    """Parse raw metrics data"""
    if not data:
        return {'spend': 0, 'revenue': 0, 'roas': 0, 'clicks': 0, 'impressions': 0, 'purchases': 0}

    spend = float(data.get('spend', 0))

    # Extract revenue and purchases from actions
    revenue = 0
    purchases = 0
    for action in data.get('action_values', []):
        if action.get('action_type') == 'purchase':
            revenue = float(action.get('value', 0))
            break
    for action in data.get('actions', []):
        if action.get('action_type') == 'purchase':
            purchases = int(float(action.get('value', 0)))
            break

    return {
        'spend': spend,
        'revenue': revenue,
        'roas': revenue / spend if spend > 0 else 0,
        'clicks': int(data.get('clicks', 0)),
        'impressions': int(data.get('impressions', 0)),
        'purchases': purchases,
        'ctr': float(data.get('clicks', 0)) / float(data.get('impressions', 1)) * 100 if data.get('impressions') else 0
    }

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Logo
    st.markdown("""
    <div class="logo">
        <span class="logo-ad">Ad</span><span class="logo-lytics">lytics</span>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("##### AGENTES")

    pages = [
        ('traffic', '📊', 'Traffic Agent', 'Meta Ads & Analytics'),
        ('design', '🎨', 'Design Agent', 'Leonardo.ai Images'),
        ('video', '🎬', 'Video Editor', 'ElevenLabs + HeyGen'),
        ('copy', '✍️', 'Copywriter', 'Copy Forge AI'),
    ]

    for page_id, icon, title, subtitle in pages:
        is_active = st.session_state.current_page == page_id
        btn_class = "nav-button active" if is_active else "nav-button"

        if st.button(f"{icon}  {title}", key=f"nav_{page_id}", use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()

    st.markdown("---")

    # Settings
    st.markdown("##### CONFIGURACOES")
    if st.button("⚙️  Settings", key="nav_settings", use_container_width=True):
        st.session_state.current_page = 'settings'
        st.rerun()

    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        logout()

    # Status
    st.markdown("---")
    creds = get_credentials()

    st.markdown("##### STATUS")
    col1, col2 = st.columns(2)
    with col1:
        if creds['meta_token']:
            st.markdown("🟢 Meta Ads")
        else:
            st.markdown("🔴 Meta Ads")
    with col2:
        if creds['whop_key']:
            st.markdown("🟢 Whop")
        else:
            st.markdown("🔴 Whop")

# =============================================================================
# MAIN CONTENT
# =============================================================================

creds = get_credentials()

# ---------- TRAFFIC AGENT PAGE ----------
if st.session_state.current_page == 'traffic':
    st.markdown("""
    <div class="page-header">
        <div>
            <h1 class="page-title">📊 Traffic Agent</h1>
            <p class="page-subtitle">Meta Ads performance & optimization</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if creds['meta_token'] and creds['meta_account']:
        # Fetch data
        campaigns = fetch_campaigns(creds['meta_account'], creds['meta_token'])
        insights = fetch_account_insights(creds['meta_account'], creds['meta_token'])
        metrics = parse_metrics(insights)

        # KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Spend", f"${metrics['spend']:,.2f}")
        with col2:
            st.metric("Revenue", f"${metrics['revenue']:,.2f}")
        with col3:
            roas_color = "🟢" if metrics['roas'] >= 2 else "🟡" if metrics['roas'] >= 1 else "🔴"
            st.metric("ROAS", f"{roas_color} {metrics['roas']:.2f}x")
        with col4:
            st.metric("Purchases", f"{metrics['purchases']}")
        with col5:
            st.metric("CTR", f"{metrics['ctr']:.2f}%")

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3 = st.tabs(["📢 Campaigns", "📈 Analytics", "🤖 AI Insights"])

        with tab1:
            st.markdown("### Active Campaigns")

            if campaigns:
                for camp in campaigns:
                    status = camp.get('effective_status', 'UNKNOWN')
                    status_badge = "badge-success" if status == "ACTIVE" else "badge-warning" if status == "PAUSED" else "badge-error"

                    # Get campaign metrics
                    camp_insights = camp.get('insights', {}).get('data', [{}])[0] if camp.get('insights') else {}
                    camp_spend = float(camp_insights.get('spend', 0))

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{camp['name']}**")
                    with col2:
                        st.markdown(f"<span class='badge {status_badge}'>{status}</span>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"${camp_spend:,.2f}")
            else:
                st.info("No campaigns found")

        with tab2:
            st.markdown("### Performance Overview")

            # Simple chart
            if metrics['spend'] > 0:
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=metrics['roas'],
                    title={'text': "ROAS"},
                    gauge={
                        'axis': {'range': [0, 5]},
                        'bar': {'color': "#0066FF"},
                        'steps': [
                            {'range': [0, 1], 'color': "#EF4444"},
                            {'range': [1, 2], 'color': "#F59E0B"},
                            {'range': [2, 5], 'color': "#10B981"}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 2},
                            'thickness': 0.75,
                            'value': metrics['roas']
                        }
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F8FAFC'},
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.markdown("### AI Recommendations")

            # Generate simple AI insights
            if metrics['roas'] < 1.5:
                st.markdown("""
                <div class="card" style="border-left: 4px solid #EF4444;">
                    <h4>⚠️ Low ROAS Alert</h4>
                    <p>Your ROAS is below 1.5x. Consider pausing underperforming campaigns and reallocating budget to top performers.</p>
                </div>
                """, unsafe_allow_html=True)

            if metrics['ctr'] < 1:
                st.markdown("""
                <div class="card" style="border-left: 4px solid #F59E0B;">
                    <h4>📊 CTR Optimization</h4>
                    <p>CTR is below 1%. Test new creatives and ad copy to improve engagement.</p>
                </div>
                """, unsafe_allow_html=True)

            if metrics['roas'] >= 2:
                st.markdown("""
                <div class="card" style="border-left: 4px solid #10B981;">
                    <h4>✅ Strong Performance</h4>
                    <p>ROAS is healthy at {:.2f}x. Consider scaling budget by 20% on top campaigns.</p>
                </div>
                """.format(metrics['roas']), unsafe_allow_html=True)
    else:
        st.warning("Configure META_ACCESS_TOKEN and META_AD_ACCOUNT_ID in secrets")

# ---------- DESIGN AGENT PAGE ----------
elif st.session_state.current_page == 'design':
    st.markdown("""
    <div class="page-header">
        <div>
            <h1 class="page-title">🎨 Design Agent</h1>
            <p class="page-subtitle">AI-powered image generation with Leonardo.ai</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Generate Image")
        prompt = st.text_area("Describe your image", placeholder="A professional product photo of a luxury watch on marble surface, studio lighting, 8k quality", height=100)

        col_a, col_b = st.columns(2)
        with col_a:
            aspect = st.selectbox("Aspect Ratio", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"])
        with col_b:
            style = st.selectbox("Style", ["Photorealistic", "Digital Art", "3D Render", "Illustration"])

        if st.button("🎨 Generate Image", use_container_width=True):
            st.info("Leonardo.ai integration - Configure LEONARDO_API_KEY")

    with col2:
        st.markdown("### Recent Generations")
        st.markdown("""
        <div class="card">
            <p style="color: #94A3B8 !important; text-align: center;">No recent images</p>
        </div>
        """, unsafe_allow_html=True)

# ---------- VIDEO EDITOR PAGE ----------
elif st.session_state.current_page == 'video':
    st.markdown("""
    <div class="page-header">
        <div>
            <h1 class="page-title">🎬 Video Editor</h1>
            <p class="page-subtitle">AI videos with ElevenLabs voice + HeyGen avatars</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎤 Voice Generation", "👤 Avatar Video", "📁 Library"])

    with tab1:
        st.markdown("### Generate Voice")
        script = st.text_area("Script", placeholder="Enter the text you want to convert to speech...", height=150)

        col1, col2 = st.columns(2)
        with col1:
            voice = st.selectbox("Voice", ["Select voice...", "Professional Male", "Professional Female", "Custom Clone"])
        with col2:
            language = st.selectbox("Language", ["English", "Portuguese", "Spanish"])

        if st.button("🎤 Generate Audio", use_container_width=True):
            st.info("ElevenLabs integration - Configure ELEVENLABS_API_KEY")

    with tab2:
        st.markdown("### Create Avatar Video")

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Select Avatar", ["Select avatar...", "Custom Avatar 1", "Stock Avatar"])
        with col2:
            st.selectbox("Video Format", ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)"])

        st.text_area("Script for Avatar", placeholder="What should the avatar say?", height=100)

        if st.button("🎬 Generate Video", use_container_width=True):
            st.info("HeyGen integration - Configure HEYGEN_API_KEY")

    with tab3:
        st.markdown("### Video Library")
        st.info("No videos generated yet")

# ---------- COPYWRITER PAGE ----------
elif st.session_state.current_page == 'copy':
    st.markdown("""
    <div class="page-header">
        <div>
            <h1 class="page-title">✍️ Copywriter</h1>
            <p class="page-subtitle">AI-powered ad copy generation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Generate Copy")

        product = st.text_input("Product/Service", placeholder="e.g., Online course about digital marketing")
        target = st.text_input("Target Audience", placeholder="e.g., Entrepreneurs aged 25-45")
        tone = st.selectbox("Tone", ["Professional", "Casual", "Urgent", "Inspirational", "Educational"])

        copy_type = st.selectbox("Copy Type", [
            "Facebook Ad - Primary Text",
            "Facebook Ad - Headline",
            "Instagram Story",
            "Email Subject Lines",
            "Landing Page Headline"
        ])

        if st.button("✍️ Generate Copy", use_container_width=True):
            # Placeholder for AI copy generation
            st.markdown("""
            <div class="card" style="border-left: 4px solid #0066FF;">
                <h4>Generated Copy</h4>
                <p>🚀 Transform your business in 30 days!</p>
                <p>Join 10,000+ entrepreneurs who discovered the secret to scaling their digital presence.</p>
                <p>✅ Proven strategies<br>✅ Step-by-step guidance<br>✅ Real results</p>
                <p><strong>Start your journey today →</strong></p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Copy Templates")
        templates = ["AIDA Formula", "PAS Formula", "Before-After-Bridge", "4 Ps", "Storytelling"]
        for t in templates:
            st.markdown(f"""
            <div class="card" style="padding: 12px; cursor: pointer;">
                <p style="margin: 0;">{t}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------- SETTINGS PAGE ----------
elif st.session_state.current_page == 'settings':
    st.markdown("""
    <div class="page-header">
        <div>
            <h1 class="page-title">⚙️ Settings</h1>
            <p class="page-subtitle">Configure your integrations</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### API Connections")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <h4>📊 Meta Ads</h4>
            <p>Status: {} Connected</p>
        </div>
        """.format("🟢" if creds['meta_token'] else "🔴 Not"), unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h4>🎨 Leonardo.ai</h4>
            <p>Status: 🔴 Not Connected</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h4>🎤 ElevenLabs</h4>
            <p>Status: 🔴 Not Connected</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h4>👤 HeyGen</h4>
            <p>Status: 🔴 Not Connected</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("Configure API keys in Streamlit Cloud secrets or .streamlit/secrets.toml")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748B !important; font-size: 12px;">
    Adlytics v3.0 · {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
""", unsafe_allow_html=True)
