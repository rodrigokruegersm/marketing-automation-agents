"""
Brez Scales - Paid Challenge Funnel Dashboard
Design System: Clean, Professional, High Contrast
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Brez Scales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# DESIGN SYSTEM - Senior Designer Approach
# =============================================================================
# Color Palette:
#   Primary: #0066FF (Blue)
#   Success: #00C853 (Green)
#   Danger:  #FF3D00 (Red/Orange)
#   Warning: #FFB300 (Amber)
#   Dark:    #1A1A2E (Near Black)
#   Light:   #F5F7FA (Light Gray)
#   White:   #FFFFFF
#
# Typography:
#   Headers: Bold, larger sizes
#   Body: Regular weight, high contrast
#   Numbers: Monospace for alignment
# =============================================================================

st.markdown("""
<style>
    /* ========================================
       RESET & BASE STYLES
       ======================================== */

    /* Force light theme */
    .stApp {
        background-color: #F5F7FA !important;
    }

    /* Remove default padding */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }

    /* ========================================
       TYPOGRAPHY
       ======================================== */

    /* All text should be dark */
    * {
        color: #1A1A2E !important;
    }

    h1, h2, h3 {
        color: #1A1A2E !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    h1 { font-size: 2.25rem !important; }
    h2 { font-size: 1.5rem !important; margin-top: 2rem !important; }
    h3 { font-size: 1.125rem !important; }

    /* ========================================
       METRIC CARDS - Primary KPIs
       ======================================== */

    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    }

    /* Metric Label */
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #6B7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {
        color: #6B7280 !important;
    }

    /* Metric Value */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #1A1A2E !important;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace !important;
    }

    [data-testid="stMetricValue"] > div {
        color: #1A1A2E !important;
    }

    /* Metric Delta */
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricDelta"] > div {
        color: inherit !important;
    }

    /* ========================================
       SIDEBAR
       ======================================== */

    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }

    [data-testid="stSidebar"] * {
        color: #1A1A2E !important;
    }

    /* ========================================
       DIVIDERS
       ======================================== */

    hr {
        border: none !important;
        height: 1px !important;
        background: #E5E7EB !important;
        margin: 2rem 0 !important;
    }

    /* ========================================
       CHARTS CONTAINER
       ======================================== */

    .chart-container {
        background: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }

    /* ========================================
       INFO/ALERT BOXES
       ======================================== */

    .stAlert {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        border-left: 4px solid #0066FF !important;
    }

    .stAlert * {
        color: #1A1A2E !important;
    }

    /* ========================================
       PROGRESS BARS
       ======================================== */

    .stProgress > div > div {
        background: #E5E7EB !important;
        border-radius: 4px !important;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #0066FF, #00C853) !important;
        border-radius: 4px !important;
    }

    /* ========================================
       EXPANDER
       ======================================== */

    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E5E7EB !important;
    }

    /* ========================================
       CUSTOM CLASSES
       ======================================== */

    .kpi-hero {
        background: linear-gradient(135deg, #0066FF 0%, #0052CC 100%) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        color: white !important;
        text-align: center !important;
    }

    .kpi-hero * {
        color: white !important;
    }

    .section-header {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin-bottom: 1rem !important;
    }

    .status-good { color: #00C853 !important; }
    .status-warning { color: #FFB300 !important; }
    .status-bad { color: #FF3D00 !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# API CONFIGURATION
# =============================================================================

META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', 'EAARxSEanVtUBQfauZBuy1WI8Luaq4A9pj4pD7N6dUvaL9aPCorg8W2G5dDpdyze2OtLVc8RnGxNazo1ri1mHNwNY54Dk1AE6HTLBFxQnIwl6j9qU3eFzhzxHT9k08Qx2E5lopXDmcfNPcZCdWobZC4j0wuHjNsd2ONMTLQu2XU0q9iaZClBjtAl16CGYYgZDZD')
META_AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID', 'act_1202800550735727')

# =============================================================================
# DATA FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def fetch_meta_data(date_preset='last_7d'):
    """Fetch data from Meta Ads API"""
    url = f"https://graph.facebook.com/v18.0/{META_AD_ACCOUNT_ID}/insights"
    params = {
        'fields': 'spend,impressions,reach,frequency,cpm,clicks,cpc,ctr,actions,action_values,cost_per_action_type,purchase_roas',
        'date_preset': date_preset,
        'access_token': META_ACCESS_TOKEN
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def extract_action_value(actions, action_type):
    """Extract value from actions array"""
    if not actions:
        return 0
    for action in actions:
        if action.get('action_type') == action_type:
            return float(action.get('value', 0))
    return 0

def parse_meta_data(raw_data):
    """Parse raw Meta data into structured format"""
    if not raw_data:
        return None

    actions = raw_data.get('actions', [])
    action_values = raw_data.get('action_values', [])
    cost_per_action = raw_data.get('cost_per_action_type', [])

    return {
        'spend': float(raw_data.get('spend', 0)),
        'impressions': int(raw_data.get('impressions', 0)),
        'reach': int(raw_data.get('reach', 0)),
        'frequency': float(raw_data.get('frequency', 0)),
        'cpm': float(raw_data.get('cpm', 0)),
        'clicks': int(raw_data.get('clicks', 0)),
        'cpc': float(raw_data.get('cpc', 0)),
        'ctr': float(raw_data.get('ctr', 0)),
        'link_clicks': extract_action_value(actions, 'link_click'),
        'lp_views': extract_action_value(actions, 'landing_page_view'),
        'init_checkout': extract_action_value(actions, 'initiate_checkout'),
        'add_payment': extract_action_value(actions, 'add_payment_info'),
        'purchases': extract_action_value(actions, 'purchase'),
        'revenue': extract_action_value(action_values, 'purchase'),
        'cpp': extract_action_value(cost_per_action, 'purchase'),
        'roas': float(raw_data.get('purchase_roas', [{}])[0].get('value', 0)) if raw_data.get('purchase_roas') else 0
    }

# =============================================================================
# DASHBOARD LAYOUT
# =============================================================================

# Header Row
col_title, col_controls = st.columns([3, 1])

with col_title:
    st.markdown("# 📊 Brez Scales")
    st.caption("Paid Challenge Funnel · Meta Ads Performance")

with col_controls:
    date_preset = st.selectbox(
        "Period",
        options=['yesterday', 'last_3d', 'last_7d', 'last_14d', 'last_30d'],
        index=2,
        format_func=lambda x: {
            'yesterday': '📅 Yesterday',
            'last_3d': '📅 Last 3 Days',
            'last_7d': '📅 Last 7 Days',
            'last_14d': '📅 Last 14 Days',
            'last_30d': '📅 Last 30 Days'
        }.get(x, x),
        label_visibility="collapsed"
    )

st.divider()

# Fetch Data
with st.spinner("Loading data from Meta Ads..."):
    raw_data = fetch_meta_data(date_preset)
    data = parse_meta_data(raw_data)

if data:
    # Calculate derived metrics
    profit = data['revenue'] - data['spend']
    margin = (profit / data['revenue'] * 100) if data['revenue'] > 0 else 0
    commission = profit * 0.20
    aov = data['revenue'] / data['purchases'] if data['purchases'] > 0 else 0

    # =========================================================================
    # SECTION 1: HERO KPIs (Most Important)
    # =========================================================================

    st.markdown("### 🎯 Key Performance Indicators")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        roas_status = "✓ Good" if data['roas'] >= 2 else "⚠ Low"
        st.metric(
            label="ROAS",
            value=f"{data['roas']:.2f}x",
            delta=roas_status,
            delta_color="normal" if data['roas'] >= 2 else "inverse"
        )

    with kpi2:
        st.metric(
            label="REVENUE",
            value=f"${data['revenue']:,.0f}",
            delta=f"${profit:,.0f} profit"
        )

    with kpi3:
        st.metric(
            label="AD SPEND",
            value=f"${data['spend']:,.0f}",
            delta=f"{margin:.0f}% margin"
        )

    with kpi4:
        cpp_status = "✓ Good" if data['cpp'] < 20 else "⚠ High"
        st.metric(
            label="COST/PURCHASE",
            value=f"${data['cpp']:.2f}",
            delta=cpp_status,
            delta_color="normal" if data['cpp'] < 20 else "inverse"
        )

    st.divider()

    # =========================================================================
    # SECTION 2: CHARTS
    # =========================================================================

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### 💰 Revenue Breakdown")

        # Donut Chart for Revenue vs Spend
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Ad Spend', 'Profit'],
            values=[data['spend'], profit],
            hole=0.65,
            marker_colors=['#FF6B6B', '#00C853'],
            textinfo='label+percent',
            textfont=dict(size=14, color='#1A1A2E'),
            hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>"
        )])

        fig_donut.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text=f'<b>${data["revenue"]:,.0f}</b><br><span style="font-size:12px">Revenue</span>',
                x=0.5, y=0.5,
                font_size=20,
                font_color='#1A1A2E',
                showarrow=False
            )]
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.markdown("### 🔄 Conversion Funnel")

        # Funnel Chart
        funnel_stages = ['Impressions', 'Clicks', 'LP Views', 'Checkouts', 'Purchases']
        funnel_values = [
            data['impressions'],
            data['clicks'],
            int(data['lp_views']),
            int(data['init_checkout']),
            int(data['purchases'])
        ]

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textposition="auto",
            texttemplate="%{value:,}",
            textfont=dict(size=14, color='white'),
            marker=dict(
                color=['#0066FF', '#3385FF', '#66A3FF', '#99C2FF', '#00C853'],
                line=dict(width=0)
            ),
            connector=dict(line=dict(color='#E5E7EB', width=1))
        ))

        fig_funnel.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1A1A2E')
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

    st.divider()

    # =========================================================================
    # SECTION 3: DETAILED METRICS
    # =========================================================================

    st.markdown("### 📈 Media Buying Metrics")

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.metric("CTR", f"{data['ctr']:.2f}%")
    with m2:
        st.metric("CPC", f"${data['cpc']:.2f}")
    with m3:
        st.metric("CPM", f"${data['cpm']:.2f}")
    with m4:
        freq_delta = "⚠ Watch" if data['frequency'] > 2.5 else "✓ OK"
        st.metric("Frequency", f"{data['frequency']:.2f}", delta=freq_delta,
                  delta_color="inverse" if data['frequency'] > 2.5 else "off")
    with m5:
        st.metric("Reach", f"{data['reach']:,}")
    with m6:
        st.metric("Purchases", f"{int(data['purchases']):,}")

    st.divider()

    # =========================================================================
    # SECTION 4: FUNNEL RATES
    # =========================================================================

    st.markdown("### 🎯 Conversion Rates")

    # Calculate rates
    ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
    lp_rate = (data['lp_views'] / data['clicks'] * 100) if data['clicks'] > 0 else 0
    ic_rate = (data['init_checkout'] / data['lp_views'] * 100) if data['lp_views'] > 0 else 0
    close_rate = (data['purchases'] / data['init_checkout'] * 100) if data['init_checkout'] > 0 else 0

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown("**Impression → Click**")
        st.markdown(f"<h2 style='margin:0;color:#0066FF'>{ctr:.2f}%</h2>", unsafe_allow_html=True)
        st.progress(min(ctr / 5, 1.0))
        st.caption("Target: >2%")

    with r2:
        st.markdown("**Click → Landing Page**")
        st.markdown(f"<h2 style='margin:0;color:#0066FF'>{lp_rate:.1f}%</h2>", unsafe_allow_html=True)
        st.progress(min(lp_rate / 100, 1.0))
        st.caption("Target: >40%")

    with r3:
        st.markdown("**LP → Checkout**")
        st.markdown(f"<h2 style='margin:0;color:#0066FF'>{ic_rate:.1f}%</h2>", unsafe_allow_html=True)
        st.progress(min(ic_rate / 15, 1.0))
        st.caption("Target: >5%")

    with r4:
        st.markdown("**Checkout → Purchase**")
        st.markdown(f"<h2 style='margin:0;color:#00C853'>{close_rate:.1f}%</h2>", unsafe_allow_html=True)
        st.progress(min(close_rate / 100, 1.0))
        st.caption("Target: >50%")

    st.divider()

    # =========================================================================
    # SECTION 5: FINANCIAL SUMMARY
    # =========================================================================

    st.markdown("### 💼 Agency Commission")

    days_map = {'yesterday': 1, 'last_3d': 3, 'last_7d': 7, 'last_14d': 14, 'last_30d': 30}
    days = days_map.get(date_preset, 7)
    daily_commission = commission / days

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.metric("Period Profit", f"${profit:,.2f}")
    with f2:
        st.metric("Commission (20%)", f"${commission:,.2f}")
    with f3:
        st.metric("Weekly Projection", f"${daily_commission * 7:,.2f}")
    with f4:
        st.metric("Monthly Projection", f"${daily_commission * 30:,.2f}")

    st.divider()

    # =========================================================================
    # SECTION 6: ALERTS
    # =========================================================================

    st.markdown("### ⚠️ Alerts & Actions")

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        if data['frequency'] > 2.5:
            st.error(f"🔴 **High Frequency** ({data['frequency']:.2f}) - Prepare new creatives")
        elif data['frequency'] > 2:
            st.warning(f"🟡 **Watch Frequency** ({data['frequency']:.2f}) - Monitor closely")
        else:
            st.success(f"🟢 **Frequency OK** ({data['frequency']:.2f})")

    with alert_col2:
        if data['roas'] >= 2.5:
            st.success(f"🟢 **Strong ROAS** ({data['roas']:.2f}x) - Consider scaling 20%")
        elif data['roas'] >= 2:
            st.info(f"🔵 **Good ROAS** ({data['roas']:.2f}x) - Maintain current")
        else:
            st.error(f"🔴 **Low ROAS** ({data['roas']:.2f}x) - Review campaigns")

    # Raw Data Expander
    with st.expander("📋 Raw API Data"):
        st.json(raw_data)

else:
    st.error("❌ Could not load data from Meta Ads API")
    st.info("Check that META_ACCESS_TOKEN and META_AD_ACCOUNT_ID are configured correctly.")

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Account: {META_AD_ACCOUNT_ID}")
