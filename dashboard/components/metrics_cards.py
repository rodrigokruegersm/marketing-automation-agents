"""
Metrics Cards Components
KPI display cards and metric visualizations
"""

import streamlit as st
from typing import Dict, List, Optional


def render_metrics_overview(metrics: Dict, thresholds: Optional[Dict] = None):
    """
    Render main KPI overview cards.

    Args:
        metrics: Dictionary with spend, revenue, roas, cpp, etc.
        thresholds: Optional thresholds for status indicators
    """
    if not metrics:
        st.warning("Sem dados de metricas disponiveis.")
        return

    thresholds = thresholds or {
        'roas': {'excellent': 2.5, 'good': 2.0, 'warning': 1.5},
        'cpp': {'excellent': 12, 'good': 18, 'warning': 25},
        'frequency': {'excellent': 1.5, 'good': 2.0, 'warning': 2.5},
        'ctr': {'excellent': 2.5, 'good': 1.5, 'warning': 1.0}
    }

    # Row 1: Financial KPIs
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        roas = metrics.get('roas', 0)
        roas_status = _get_status(roas, thresholds['roas'], higher_is_better=True)
        st.metric(
            "ROAS",
            f"{roas:.2f}x",
            f"{roas_status['icon']} {roas_status['label']}"
        )

    with k2:
        revenue = metrics.get('revenue', 0)
        profit = metrics.get('profit', 0)
        st.metric(
            "Revenue",
            f"${revenue:,.0f}",
            f"${profit:,.0f} profit"
        )

    with k3:
        spend = metrics.get('spend', 0)
        st.metric("Ad Spend", f"${spend:,.0f}")

    with k4:
        cpp = metrics.get('cpp', 0)
        cpp_status = _get_status(cpp, thresholds['cpp'], higher_is_better=False)
        st.metric(
            "CPP",
            f"${cpp:.2f}",
            f"{cpp_status['icon']} {cpp_status['label']}"
        )

    # Row 2: Performance KPIs
    k5, k6, k7, k8 = st.columns(4)

    with k5:
        purchases = metrics.get('purchases', 0)
        st.metric("Purchases", f"{int(purchases)}")

    with k6:
        frequency = metrics.get('frequency', 0)
        freq_status = _get_status(frequency, thresholds['frequency'], higher_is_better=False)
        st.metric(
            "Frequency",
            f"{frequency:.2f}",
            f"{freq_status['icon']} {freq_status['label']}"
        )

    with k7:
        ctr = metrics.get('ctr', 0)
        ctr_status = _get_status(ctr, thresholds['ctr'], higher_is_better=True)
        st.metric(
            "CTR",
            f"{ctr:.2f}%",
            f"{ctr_status['icon']} {ctr_status['label']}"
        )

    with k8:
        leads = metrics.get('leads', 0)
        cpl = metrics.get('cpl', 0)
        if leads > 0:
            st.metric("Leads", f"{int(leads)}", f"${cpl:.2f} CPL")
        else:
            impressions = metrics.get('impressions', 0)
            st.metric("Impressions", f"{impressions:,}")


def _get_status(value: float, thresholds: Dict, higher_is_better: bool = True) -> Dict:
    """
    Determine status based on value and thresholds.

    Returns dict with icon, label, and color.
    """
    if higher_is_better:
        if value >= thresholds.get('excellent', float('inf')):
            return {'icon': '🟢', 'label': 'Excelente', 'color': '#10B981'}
        elif value >= thresholds.get('good', float('inf')):
            return {'icon': '🟢', 'label': 'Bom', 'color': '#10B981'}
        elif value >= thresholds.get('warning', 0):
            return {'icon': '🟡', 'label': 'Atencao', 'color': '#F59E0B'}
        else:
            return {'icon': '🔴', 'label': 'Critico', 'color': '#EF4444'}
    else:
        # Lower is better (e.g., CPP, frequency)
        if value <= thresholds.get('excellent', 0):
            return {'icon': '🟢', 'label': 'Excelente', 'color': '#10B981'}
        elif value <= thresholds.get('good', 0):
            return {'icon': '🟢', 'label': 'Bom', 'color': '#10B981'}
        elif value <= thresholds.get('warning', float('inf')):
            return {'icon': '🟡', 'label': 'Atencao', 'color': '#F59E0B'}
        else:
            return {'icon': '🔴', 'label': 'Critico', 'color': '#EF4444'}


def render_funnel_metrics(funnel_data: Dict, show_alerts: bool = True):
    """
    Render metrics for a specific funnel.

    Args:
        funnel_data: FunnelData dictionary with tag, name, metrics, alerts
        show_alerts: Whether to display alerts
    """
    metrics = funnel_data.get('metrics', {})

    st.markdown(f"### {{{funnel_data.get('tag', 'Unknown')}}}")
    st.caption(funnel_data.get('name', ''))

    # Metrics row
    cols = st.columns(6)

    with cols[0]:
        st.metric("ROAS", f"{metrics.get('roas', 0):.2f}x")
    with cols[1]:
        st.metric("Spend", f"${metrics.get('spend', 0):,.0f}")
    with cols[2]:
        st.metric("Revenue", f"${metrics.get('revenue', 0):,.0f}")
    with cols[3]:
        st.metric("CPP", f"${metrics.get('cpp', 0):.2f}")
    with cols[4]:
        st.metric("Purchases", f"{int(metrics.get('purchases', 0))}")
    with cols[5]:
        st.metric("Campanhas", f"{metrics.get('active_campaigns', 0)}/{metrics.get('total_campaigns', 0)}")

    # Alerts
    if show_alerts:
        alerts = funnel_data.get('alerts', [])
        opportunities = funnel_data.get('opportunities', [])

        if alerts:
            for alert in alerts:
                st.warning(alert)

        if opportunities:
            for opp in opportunities:
                st.success(opp)


def render_mini_metrics(metrics: Dict):
    """Render compact inline metrics"""
    roas = metrics.get('roas', 0)
    spend = metrics.get('spend', 0)

    st.markdown(f"""
    <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
        <span><strong>ROAS:</strong> {roas:.2f}x</span>
        <span><strong>Spend:</strong> ${spend:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)


def render_trend_indicator(current: float, previous: float, format_str: str = "{:.2f}"):
    """Render trend arrow with percentage change"""
    if previous == 0:
        return ""

    change = ((current - previous) / previous) * 100

    if change > 0:
        return f"<span style='color: #10B981;'>↑ {change:.1f}%</span>"
    elif change < 0:
        return f"<span style='color: #EF4444;'>↓ {abs(change):.1f}%</span>"
    else:
        return "<span style='color: #64748B;'>→ 0%</span>"
