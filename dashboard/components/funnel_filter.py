"""
Funnel Filter Component
Filter campaigns by funnel tag {TAG}
"""

import streamlit as st
from typing import List, Dict, Optional


def render_funnel_filter(
    funnels: List[Dict],
    current_funnel: Optional[str] = None
) -> Optional[str]:
    """
    Render funnel filter tabs/pills.

    Args:
        funnels: List of funnel data with tag, name, type, metrics
        current_funnel: Currently selected funnel tag

    Returns:
        Selected funnel tag or None for all funnels
    """
    if not funnels:
        st.caption("Nenhum funil encontrado. Adicione {TAG} no nome das campanhas.")
        return None

    st.markdown("### 🎯 Funis Ativos")

    # Create pills/tabs for funnels
    funnel_tags = ["Todos"] + [f['tag'] for f in funnels]

    # Horizontal layout for funnel pills
    cols = st.columns(min(len(funnel_tags), 6))

    selected = current_funnel

    for idx, tag in enumerate(funnel_tags[:6]):
        with cols[idx]:
            is_active = (tag == "Todos" and current_funnel is None) or (tag == current_funnel)

            funnel_data = next((f for f in funnels if f['tag'] == tag), None)

            if tag == "Todos":
                label = "📊 Todos"
                status_color = "#6366F1"
            else:
                status = funnel_data.get('status', 'healthy') if funnel_data else 'healthy'
                status_icons = {'healthy': '🟢', 'warning': '🟡', 'critical': '🔴'}
                label = f"{status_icons.get(status, '⚪')} {tag}"
                status_color = {'healthy': '#10B981', 'warning': '#F59E0B', 'critical': '#EF4444'}.get(status, '#6366F1')

            if _render_funnel_pill(label, is_active, status_color, key=f"funnel_{tag}"):
                selected = None if tag == "Todos" else tag
                st.session_state.selected_funnel = selected
                st.rerun()

    return selected


def _render_funnel_pill(label: str, is_active: bool, color: str, key: str) -> bool:
    """Render individual funnel pill button - Clean Minimal Theme"""
    bg_color = color if is_active else "#FFFFFF"
    border_color = color if is_active else "#E2E8F0"
    text_color = "#FFFFFF" if is_active else "#1E293B"

    st.markdown(f"""
    <style>
        div[data-testid="stButton"] button[kind="secondary"][key="{key}"] {{
            background: {bg_color} !important;
            border: 1px solid {border_color} !important;
            color: {text_color} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    return st.button(label, key=key, use_container_width=True)


def render_funnel_cards(funnels: List[Dict]) -> Optional[str]:
    """
    Render funnel cards with metrics.

    Returns:
        Selected funnel tag when clicked
    """
    if not funnels:
        st.info("Configure as campanhas com {FUNNEL_TAG} no nome para ver os funis.")
        return None

    # Sort by status priority (critical first) then by spend
    status_order = {'critical': 0, 'warning': 1, 'healthy': 2}
    sorted_funnels = sorted(
        funnels,
        key=lambda x: (status_order.get(x.get('status', 'healthy'), 3), -x.get('metrics', {}).get('spend', 0))
    )

    # Create grid
    cols = st.columns(3)

    for idx, funnel in enumerate(sorted_funnels):
        with cols[idx % 3]:
            metrics = funnel.get('metrics', {})
            status = funnel.get('status', 'healthy')

            # Clean Minimal theme - white backgrounds with colored accents
            status_colors = {
                'healthy': ('#10B981', '#ECFDF5', '#065F46'),
                'warning': ('#F59E0B', '#FFFBEB', '#92400E'),
                'critical': ('#EF4444', '#FEF2F2', '#991B1B')
            }
            accent, bg, text = status_colors.get(status, ('#0066FF', '#FFFFFF', '#1E293B'))

            roas = metrics.get('roas', 0)
            spend = metrics.get('spend', 0)
            revenue = metrics.get('revenue', 0)
            campaigns = metrics.get('total_campaigns', 0)
            active = metrics.get('active_campaigns', 0)

            st.markdown(f"""
            <div style="
                background: {bg};
                border: 1px solid {accent};
                border-left: 4px solid {accent};
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <span style="font-weight: 700; font-size: 1rem; color: {text};">{{{{ {funnel['tag']} }}}}</span>
                    <span style="font-size: 0.75rem; color: {accent}; font-weight: 600;">{funnel.get('type', 'custom').upper()}</span>
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.5rem;">
                    {funnel.get('name', funnel['tag'])}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem;">
                    <div>
                        <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase;">ROAS</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #0A1628;">{roas:.2f}x</div>
                    </div>
                    <div>
                        <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase;">Spend</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #0A1628;">${spend:,.0f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase;">Revenue</div>
                        <div style="font-size: 1rem; color: #1E293B;">${revenue:,.0f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.65rem; color: #64748B; text-transform: uppercase;">Campanhas</div>
                        <div style="font-size: 1rem; color: #1E293B;">{active}/{campaigns}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Detalhar", key=f"detail_{funnel['tag']}", use_container_width=True):
                return funnel['tag']

    return None


def render_funnel_comparison_table(funnels: List[Dict]):
    """Render comparison table for all funnels"""
    if not funnels:
        return

    st.markdown("### 📊 Comparativo de Funis")

    import pandas as pd

    data = []
    for f in funnels:
        m = f.get('metrics', {})
        data.append({
            'Funil': f['tag'],
            'Tipo': f.get('type', '-'),
            'Status': f.get('status', '-'),
            'ROAS': f"{m.get('roas', 0):.2f}x",
            'Spend': f"${m.get('spend', 0):,.0f}",
            'Revenue': f"${m.get('revenue', 0):,.0f}",
            'Profit': f"${m.get('profit', 0):,.0f}",
            'CPP': f"${m.get('cpp', 0):.2f}",
            'Campanhas': m.get('total_campaigns', 0)
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
