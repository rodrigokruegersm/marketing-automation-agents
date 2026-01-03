"""
Navigation Components
Fluid navigation between clients, funnels, and campaigns
"""

import streamlit as st
from typing import List, Dict, Optional


def render_navigation(
    clients: List[Dict],
    current_client: Optional[str] = None,
    current_funnel: Optional[str] = None,
    current_view: str = "overview"
) -> Dict:
    """
    Render the main navigation breadcrumb and controls.

    Returns:
        Dict with navigation state: client, funnel, view
    """
    nav_state = {
        'client': current_client,
        'funnel': current_funnel,
        'view': current_view
    }

    # Breadcrumb style navigation
    breadcrumb_parts = []

    if current_client:
        client_name = next((c['name'] for c in clients if c['slug'] == current_client), current_client)
        breadcrumb_parts.append(f"**{client_name}**")

        if current_funnel:
            breadcrumb_parts.append(f" → {current_funnel}")
    else:
        breadcrumb_parts.append("**Todos os Clientes**")

    # Render breadcrumb
    st.markdown(
        f"<div style='font-size: 0.875rem; color: #64748B; margin-bottom: 1rem;'>"
        f"{''.join(breadcrumb_parts)}</div>",
        unsafe_allow_html=True
    )

    return nav_state


def render_quick_switcher(
    clients: List[Dict],
    funnels: List[Dict],
    current_client: Optional[str] = None,
    current_funnel: Optional[str] = None
) -> Dict:
    """
    Render quick switcher for rapid navigation.

    Returns:
        Dict with selected client and funnel
    """
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            # Client selector
            client_options = ["Todos os Clientes"] + [c['name'] for c in clients]
            client_slugs = [None] + [c['slug'] for c in clients]

            current_idx = 0
            if current_client:
                try:
                    current_idx = client_slugs.index(current_client)
                except ValueError:
                    current_idx = 0

            selected_client_name = st.selectbox(
                "Cliente",
                options=client_options,
                index=current_idx,
                key="quick_client"
            )

            selected_client = client_slugs[client_options.index(selected_client_name)]

        with col2:
            # Funnel selector (filtered by client)
            if funnels:
                funnel_options = ["Todos os Funis"] + [f['tag'] for f in funnels]

                current_funnel_idx = 0
                if current_funnel and current_funnel in funnel_options:
                    current_funnel_idx = funnel_options.index(current_funnel)

                selected_funnel = st.selectbox(
                    "Funil",
                    options=funnel_options,
                    index=current_funnel_idx,
                    key="quick_funnel"
                )

                if selected_funnel == "Todos os Funis":
                    selected_funnel = None
            else:
                st.selectbox("Funil", options=["Sem funis"], disabled=True)
                selected_funnel = None

        with col3:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            if st.button("🔄", help="Atualizar dados"):
                st.cache_data.clear()
                st.rerun()

    return {
        'client': selected_client,
        'funnel': selected_funnel
    }


def render_view_tabs() -> str:
    """
    Render view selection tabs.

    Returns:
        Selected view name
    """
    views = {
        "overview": "📊 Overview",
        "campaigns": "📢 Campanhas",
        "funnels": "🎯 Funis",
        "ai": "🤖 IA Insights",
        "settings": "⚙️ Config"
    }

    tabs = st.tabs(list(views.values()))

    # Return the selected view based on which tab is active
    # Note: Streamlit doesn't provide direct tab selection state,
    # so we use session state to track it
    return list(views.keys())[0]  # Default to overview
