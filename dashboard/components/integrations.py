"""
Integrations Components
UI components for managing platform integrations (Checkout, Hyros, etc.)
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime


def render_integration_status(integrations: Dict[str, Dict]) -> None:
    """
    Render status cards for all integrations.

    Args:
        integrations: Dict with integration status for each platform
    """
    st.markdown("### Status das Integracoes")

    cols = st.columns(len(integrations) if integrations else 1)

    for idx, (name, status) in enumerate(integrations.items()):
        with cols[idx]:
            is_connected = status.get('connected', False)
            icon = "🟢" if is_connected else "🔴"
            status_text = "Conectado" if is_connected else "Desconectado"

            st.markdown(f"""
            <div class="integration-card {'integration-connected' if is_connected else 'integration-disconnected'}">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">{status.get('icon', '🔌')}</span>
                    <div>
                        <strong>{name}</strong><br>
                        <small>{icon} {status_text}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_checkout_metrics(checkout_data: Dict) -> None:
    """
    Render checkout platform metrics.

    Args:
        checkout_data: Dict with checkout metrics from adapters
    """
    if not checkout_data:
        st.info("Conecte uma plataforma de checkout para ver metricas de vendas.")
        return

    st.markdown("### Metricas de Checkout")

    # Summary metrics
    total_sales = checkout_data.get('total_sales', 0)
    gross_revenue = checkout_data.get('gross_revenue', 0)
    net_revenue = checkout_data.get('net_revenue', 0)
    refund_rate = checkout_data.get('refund_rate', 0)
    avg_ticket = checkout_data.get('average_ticket', 0)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Vendas", f"{total_sales}")
    with c2:
        st.metric("Faturamento Bruto", f"${gross_revenue:,.0f}")
    with c3:
        st.metric("Receita Liquida", f"${net_revenue:,.0f}")
    with c4:
        st.metric("Ticket Medio", f"${avg_ticket:,.2f}")
    with c5:
        refund_status = "🟢" if refund_rate < 3 else ("🟡" if refund_rate < 5 else "🔴")
        st.metric("Taxa Reembolso", f"{refund_rate:.1f}%", refund_status)


def render_checkout_by_funnel(by_funnel: Dict[str, Dict]) -> None:
    """
    Render checkout metrics grouped by funnel.

    Args:
        by_funnel: Dict mapping funnel_tag to sales/revenue data
    """
    if not by_funnel:
        return

    st.markdown("### Vendas por Funil")

    for funnel_tag, data in by_funnel.items():
        sales = data.get('sales', 0)
        revenue = data.get('revenue', 0)

        st.markdown(f"""
        <div class="funnel-sales-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><strong>{{{funnel_tag}}}</strong></span>
                <span>{sales} vendas | ${revenue:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_product_card(product: Dict) -> None:
    """
    Render a product card with pricing and CPP thresholds.

    Args:
        product: Product data dict
    """
    name = product.get('name', 'Produto')
    price = product.get('price', 0)
    platform = product.get('platform', 'unknown')
    funnel_tag = product.get('funnel_tag', '')
    breakeven_cpp = product.get('breakeven_cpp', 0)
    target_cpp = product.get('target_cpp', 0)

    platform_icons = {
        'whop': '🌐',
        'clickfunnels': '🔵',
        'hotmart': '🔥',
        'kiwify': '🥝',
        'stripe': '💳'
    }

    icon = platform_icons.get(platform, '📦')

    st.markdown(f"""
    <div class="product-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <span style="font-size: 1.5rem;">{icon}</span>
                <strong style="margin-left: 0.5rem;">{name}</strong>
                <span class="platform-badge">{platform.upper()}</span>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: bold;">${price:,.2f}</div>
            </div>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 2rem;">
            <div>
                <small style="color: #64748B;">Funil</small><br>
                <strong style="color: #1E293B;">{{{funnel_tag}}}</strong> if funnel_tag else <em style="color: #64748B;">Nao mapeado</em>
            </div>
            <div>
                <small style="color: #64748B;">CPP Breakeven</small><br>
                <strong style="color: #DC2626;">${breakeven_cpp:,.2f}</strong>
            </div>
            <div>
                <small style="color: #64748B;">CPP Target</small><br>
                <strong style="color: #059669;">${target_cpp:,.2f}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_cpp_analysis(
    current_cpp: float,
    product_price: float,
    breakeven_cpp: float,
    target_cpp: float
) -> None:
    """
    Render product-aware CPP analysis visualization.

    Args:
        current_cpp: Current cost per purchase
        product_price: Product sale price
        breakeven_cpp: Maximum CPP before losing money
        target_cpp: Target CPP for desired ROAS
    """
    if current_cpp <= 0:
        st.info("Sem dados de CPP disponiveis.")
        return

    # Determine status
    if current_cpp <= target_cpp:
        status = "excellent"
        status_icon = "🟢"
        status_text = "Excelente"
        margin = target_cpp - current_cpp
        msg = f"CPP ${margin:.2f} abaixo do target. Escalar!"
    elif current_cpp <= breakeven_cpp:
        status = "good"
        status_icon = "🟢"
        status_text = "Saudavel"
        margin = breakeven_cpp - current_cpp
        msg = f"Margem de ${margin:.2f} ate breakeven."
    elif current_cpp <= breakeven_cpp * 1.2:
        status = "warning"
        status_icon = "🟡"
        status_text = "Atencao"
        excess = current_cpp - breakeven_cpp
        msg = f"CPP ${excess:.2f} acima do breakeven! Otimizar."
    else:
        status = "critical"
        status_icon = "🔴"
        status_text = "Critico"
        excess = current_cpp - breakeven_cpp
        msg = f"CPP ${excess:.2f} ACIMA DO BREAKEVEN! Pausar urgente."

    st.markdown(f"""
    <div class="cpp-analysis cpp-{status}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">{status_icon} Analise CPP: {status_text}</h3>
                <p style="margin: 0.5rem 0; opacity: 0.9;">{msg}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2rem; font-weight: bold;">${current_cpp:.2f}</div>
                <small>CPP Atual</small>
            </div>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 1rem;">
            <div class="cpp-threshold">
                <small>Produto</small><br>
                <strong>${product_price:,.0f}</strong>
            </div>
            <div class="cpp-threshold">
                <small>Target CPP</small><br>
                <strong style="color: #10B981;">${target_cpp:.2f}</strong>
            </div>
            <div class="cpp-threshold">
                <small>Breakeven CPP</small><br>
                <strong style="color: #F59E0B;">${breakeven_cpp:.2f}</strong>
            </div>
            <div class="cpp-threshold">
                <small>Margem/Excesso</small><br>
                <strong>${abs(breakeven_cpp - current_cpp):.2f}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hyros_attribution(attribution_data: Dict) -> None:
    """
    Render Hyros attribution data.

    Args:
        attribution_data: Dict with attribution metrics from Hyros
    """
    if not attribution_data or 'error' in attribution_data:
        st.info("Conecte o Hyros para ver dados de atribuicao.")
        return

    st.markdown("### Atribuicao Hyros")

    # Attribution summary
    total_attributed = attribution_data.get('total_attributed_revenue', 0)
    attribution_window = attribution_data.get('attribution_window', 7)

    st.metric(
        f"Revenue Atribuido ({attribution_window}d)",
        f"${total_attributed:,.0f}"
    )

    # By source
    by_source = attribution_data.get('by_source', {})
    if by_source:
        st.markdown("**Por Fonte:**")
        for source, data in by_source.items():
            revenue = data.get('revenue', 0)
            conversions = data.get('conversions', 0)
            st.markdown(f"- **{source}**: ${revenue:,.0f} ({conversions} conversoes)")


def render_integration_settings() -> Dict[str, Any]:
    """
    Render integration settings form.

    Returns:
        Dict with configured credentials
    """
    st.markdown("### Configurar Integracoes")

    settings = {}

    # Meta Ads
    with st.expander("Meta Ads", expanded=True):
        st.markdown("**Configuracao Meta Ads API**")
        settings['meta'] = {
            'access_token': st.text_input(
                "Access Token",
                type="password",
                key="meta_token",
                help="Token de acesso da API do Meta Ads"
            ),
            'ad_account_id': st.text_input(
                "Ad Account ID",
                key="meta_account",
                help="ID da conta de anuncios (formato: act_XXXXX)"
            )
        }

    # Whop
    with st.expander("Whop"):
        st.markdown("**Configuracao Whop API**")
        settings['whop'] = {
            'api_key': st.text_input(
                "API Key",
                type="password",
                key="whop_key",
                help="Chave de API do Whop"
            ),
            'company_id': st.text_input(
                "Company ID",
                key="whop_company",
                help="ID da empresa no Whop"
            )
        }

    # ClickFunnels
    with st.expander("ClickFunnels"):
        st.markdown("**Configuracao ClickFunnels 2.0 API**")
        settings['clickfunnels'] = {
            'api_key': st.text_input(
                "API Key",
                type="password",
                key="cf_key",
                help="Chave de API do ClickFunnels"
            ),
            'workspace_id': st.text_input(
                "Workspace ID",
                key="cf_workspace",
                help="ID do workspace no ClickFunnels"
            )
        }

    # Hyros
    with st.expander("Hyros"):
        st.markdown("**Configuracao Hyros API**")
        settings['hyros'] = {
            'api_key': st.text_input(
                "API Key",
                type="password",
                key="hyros_key",
                help="Chave de API do Hyros"
            ),
            'workspace_id': st.text_input(
                "Workspace ID",
                key="hyros_workspace",
                help="ID do workspace no Hyros"
            )
        }

    return settings


def get_integration_styles() -> str:
    """Return CSS styles for integration components - Clean Minimal Theme."""
    return """
    <style>
        /* Integration Cards - White bg, dark text */
        .integration-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            color: #1E293B;
        }
        .integration-card * {
            color: #1E293B !important;
        }
        .integration-connected {
            border-left: 4px solid #10B981;
        }
        .integration-disconnected {
            border-left: 4px solid #EF4444;
        }

        /* Product Cards - White bg, dark text */
        .product-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            color: #1E293B;
        }
        .product-card * {
            color: #1E293B !important;
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

        /* CPP Analysis - White bg, dark text */
        .cpp-analysis {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #1E293B;
        }
        .cpp-analysis * {
            color: #1E293B !important;
        }
        .cpp-excellent {
            border-left: 4px solid #10B981;
            background: #ECFDF5;
        }
        .cpp-excellent * {
            color: #065F46 !important;
        }
        .cpp-good {
            border-left: 4px solid #10B981;
            background: #FFFFFF;
        }
        .cpp-warning {
            border-left: 4px solid #F59E0B;
            background: #FFFBEB;
        }
        .cpp-warning * {
            color: #92400E !important;
        }
        .cpp-critical {
            border-left: 4px solid #EF4444;
            background: #FEF2F2;
        }
        .cpp-critical * {
            color: #991B1B !important;
        }
        .cpp-threshold {
            background: #F1F5F9;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #E2E8F0;
            color: #334155 !important;
        }
        .cpp-threshold * {
            color: #334155 !important;
        }

        /* Funnel Sales Card - White bg, dark text */
        .funnel-sales-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            color: #1E293B;
        }
        .funnel-sales-card * {
            color: #1E293B !important;
        }
    </style>
    """
