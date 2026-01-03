"""
Alerts Panel Component
Display alerts and opportunities across funnels
"""

import streamlit as st
from typing import List, Dict


def render_alerts_panel(alerts_data: Dict):
    """
    Render alerts and opportunities panel.

    Args:
        alerts_data: Dictionary from DataAggregator.get_alerts_summary()
            - alerts: List of alert dicts with funnel, message, status
            - opportunities: List of opportunity dicts
            - status_counts: Dict with healthy, warning, critical counts
            - overall_status: Overall account status
    """
    st.markdown("## 🚨 Alertas e Oportunidades")

    alerts = alerts_data.get('alerts', [])
    opportunities = alerts_data.get('opportunities', [])
    status_counts = alerts_data.get('status_counts', {})
    overall = alerts_data.get('overall_status', 'healthy')

    # Status summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_colors = {'healthy': '#10B981', 'warning': '#F59E0B', 'critical': '#EF4444'}
        status_labels = {'healthy': 'Saudavel', 'warning': 'Atencao', 'critical': 'Critico'}
        st.markdown(f"""
        <div style="
            background: #FFFFFF;
            border: 2px solid {status_colors.get(overall, '#0066FF')};
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Status Geral</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {status_colors.get(overall, '#0A1628')};">
                {status_labels.get(overall, overall).upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric("🔴 Criticos", status_counts.get('critical', 0))

    with col3:
        st.metric("🟡 Atencao", status_counts.get('warning', 0))

    with col4:
        st.metric("🟢 Saudaveis", status_counts.get('healthy', 0))

    st.markdown("---")

    # Two columns: Alerts and Opportunities
    alert_col, opp_col = st.columns(2)

    with alert_col:
        st.markdown("### 🚨 Alertas")

        if alerts:
            for alert in alerts:
                status = alert.get('status', 'warning')
                funnel = alert.get('funnel', 'Unknown')
                message = alert.get('message', '')

                css_class = "alert-critical" if status == "critical" else "alert-warning"
                icon = "🔴" if status == "critical" else "🟡"

                st.markdown(f"""
                <div class="alert-item {css_class}">
                    <div class="alert-header">
                        <span>{icon} {{{funnel}}}</span>
                    </div>
                    <div class="alert-message">{message}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Nenhum alerta ativo!")

    with opp_col:
        st.markdown("### 🚀 Oportunidades")

        if opportunities:
            for opp in opportunities:
                funnel = opp.get('funnel', 'Unknown')
                message = opp.get('message', '')

                st.markdown(f"""
                <div class="opportunity-item">
                    <div class="opp-header">
                        <span>🟢 {{{funnel}}}</span>
                    </div>
                    <div class="opp-message">{message}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma oportunidade identificada no momento.")


def render_alert_styles():
    """Inject CSS styles for alerts - Clean Minimal Theme"""
    st.markdown("""
    <style>
        .alert-item, .opportunity-item {
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .alert-critical {
            background: #FEF2F2;
            border: 1px solid #EF4444;
            border-left: 4px solid #EF4444;
        }
        .alert-critical * {
            color: #991B1B !important;
        }

        .alert-warning {
            background: #FFFBEB;
            border: 1px solid #F59E0B;
            border-left: 4px solid #F59E0B;
        }
        .alert-warning * {
            color: #92400E !important;
        }

        .opportunity-item {
            background: #ECFDF5;
            border: 1px solid #10B981;
            border-left: 4px solid #10B981;
        }
        .opportunity-item * {
            color: #065F46 !important;
        }

        .alert-header, .opp-header {
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        .alert-message, .opp-message {
            font-size: 0.85rem;
            line-height: 1.4;
        }
    </style>
    """, unsafe_allow_html=True)


def render_priority_actions(alerts: List[Dict]):
    """
    Render priority action buttons for critical alerts.

    Args:
        alerts: List of alert dictionaries
    """
    critical_alerts = [a for a in alerts if a.get('status') == 'critical']

    if not critical_alerts:
        return

    st.markdown("### ⚡ Acoes Prioritarias")

    for alert in critical_alerts[:3]:  # Max 3 priority actions
        funnel = alert.get('funnel', '')
        message = alert.get('message', '')

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{{{funnel}}}**: {message}")

        with col2:
            if "ROAS" in message.upper():
                if st.button("Pausar low performers", key=f"action_roas_{funnel}"):
                    st.info("Funcionalidade em desenvolvimento")
            elif "CPP" in message.upper():
                if st.button("Revisar ad sets", key=f"action_cpp_{funnel}"):
                    st.info("Funcionalidade em desenvolvimento")
            elif "FREQUENCIA" in message.upper() or "FREQUENCY" in message.upper():
                if st.button("Expandir publico", key=f"action_freq_{funnel}"):
                    st.info("Funcionalidade em desenvolvimento")
