"""
Client Selector Component
Multi-client selection and management
"""

import streamlit as st
from typing import List, Dict, Optional


def render_client_selector(
    clients: List[Dict],
    current_client: Optional[str] = None
) -> Optional[str]:
    """
    Render client selector with cards for each client.

    Args:
        clients: List of client dictionaries with name, slug, status
        current_client: Currently selected client slug

    Returns:
        Selected client slug or None for all clients
    """
    st.markdown("### 🏢 Clientes")

    if not clients:
        st.info("Nenhum cliente configurado. Use o Client Registry para adicionar clientes.")
        return None

    # All clients option
    cols = st.columns(min(len(clients) + 1, 4))

    with cols[0]:
        all_selected = current_client is None
        _render_client_card(
            name="Todos",
            slug=None,
            status="active",
            metrics={'spend': sum(c.get('metrics', {}).get('spend', 0) for c in clients)},
            is_selected=all_selected
        )

    # Individual clients
    for idx, client in enumerate(clients[:3]):  # Max 3 + "Todos"
        with cols[idx + 1]:
            is_selected = current_client == client['slug']
            _render_client_card(
                name=client['name'],
                slug=client['slug'],
                status=client.get('status', 'active'),
                metrics=client.get('metrics', {}),
                is_selected=is_selected
            )

    # Handle selection via session state
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = current_client

    return st.session_state.selected_client


def _render_client_card(
    name: str,
    slug: Optional[str],
    status: str,
    metrics: Dict,
    is_selected: bool
):
    """Render individual client card - Clean Minimal Theme"""
    border_color = "#0066FF" if is_selected else "#E2E8F0"
    bg_color = "#EFF6FF" if is_selected else "#FFFFFF"

    status_color = "#10B981" if status == "active" else "#F59E0B"
    status_icon = "🟢" if status == "active" else "🟡"

    spend = metrics.get('spend', 0)

    card_html = f"""
    <div style="
        background: {bg_color};
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s;
        min-height: 100px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; font-size: 0.9rem; color: #0A1628;">{name}</span>
            <span style="font-size: 0.75rem;">{status_icon}</span>
        </div>
        <div style="font-size: 0.75rem; color: #64748B;">
            Spend: ${spend:,.0f}
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # Create button for selection
    if st.button(f"Selecionar", key=f"select_client_{slug or 'all'}", use_container_width=True):
        st.session_state.selected_client = slug
        st.rerun()


def render_client_grid(clients: List[Dict]) -> Optional[str]:
    """
    Render clients in a grid layout with key metrics.

    Returns:
        Selected client slug when clicked
    """
    if not clients:
        return None

    # Create 3-column grid
    rows = [clients[i:i+3] for i in range(0, len(clients), 3)]

    for row in rows:
        cols = st.columns(3)
        for idx, client in enumerate(row):
            with cols[idx]:
                metrics = client.get('metrics', {})

                st.markdown(f"""
                <div class="client-card">
                    <h4>{client['name']}</h4>
                    <div class="metrics-mini">
                        <span>ROAS: {metrics.get('roas', 0):.2f}x</span>
                        <span>Spend: ${metrics.get('spend', 0):,.0f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Ver detalhes", key=f"view_{client['slug']}"):
                    return client['slug']

    return None
