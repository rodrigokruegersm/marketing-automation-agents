"""
Dashboard Components
Reusable UI components for the unified dashboard
"""

from .navigation import render_navigation, render_quick_switcher
from .client_selector import render_client_selector
from .funnel_filter import render_funnel_filter
from .metrics_cards import render_metrics_overview, render_funnel_metrics
from .alerts_panel import render_alerts_panel
from .integrations import (
    render_integration_status,
    render_checkout_metrics,
    render_checkout_by_funnel,
    render_product_card,
    render_cpp_analysis,
    render_hyros_attribution,
    render_integration_settings,
    get_integration_styles
)

__all__ = [
    'render_navigation',
    'render_quick_switcher',
    'render_client_selector',
    'render_funnel_filter',
    'render_metrics_overview',
    'render_funnel_metrics',
    'render_alerts_panel',
    # Integrations
    'render_integration_status',
    'render_checkout_metrics',
    'render_checkout_by_funnel',
    'render_product_card',
    'render_cpp_analysis',
    'render_hyros_attribution',
    'render_integration_settings',
    'get_integration_styles'
]
